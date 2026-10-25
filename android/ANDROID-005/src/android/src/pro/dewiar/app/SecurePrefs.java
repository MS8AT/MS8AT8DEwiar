package pro.dewiar.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import android.util.Base64;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.HashMap;
import java.util.HashSet;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Секреты settings, sync_key и фонового close_watch: AES-GCM, ключ в AndroidKeyStore, ciphertext в noBackup.
 *  Чтение legacy разрешено только после шифрования и проверки. При ошибке старые данные остаются,
 *  запись блокируется до успешного чтения. Нет plaintext fallback, логов, биометрии и зависимости от Windows. */
final class SecurePrefs {
    private static final Object LOCK = new Object();
    private static final HashSet<String> BLOCKED = new HashSet<>();
    private static final int MAX_BYTES = 2 * 1024 * 1024;
    private static final int MAX_ENVELOPE = ((MAX_BYTES + 16) * 4 / 3) + 128;
    private static final String ALIAS = "ms8at.dewiar.prefs.v1";
    private final SharedPreferences legacy, state;
    private final File directory;
    private final KeySource keys;
    private final HashMap<String, String> status = new HashMap<>();

    interface KeySource { SecretKey get(boolean create) throws Exception; }

    SecurePrefs(Context context, SharedPreferences legacy) {
        this(legacy, context.getSharedPreferences("dewiar_secure_state", Context.MODE_PRIVATE),
                new File(context.getNoBackupFilesDir(), "ms8at_secure_prefs"), new AndroidKeys());
    }

    // Тесты подставляют временные prefs и JCE-ключ; production всегда использует AndroidKeys.
    SecurePrefs(SharedPreferences legacy, SharedPreferences state, File directory, KeySource keys) {
        this.legacy = legacy; this.state = state; this.directory = directory; this.keys = keys;
    }

    static boolean protects(String key) { return "settings".equals(key) || "sync_key".equals(key) || "close_watch".equals(key); }

    private static final class AndroidKeys implements KeySource {
        @Override public SecretKey get(boolean create) throws Exception {
            KeyStore store = KeyStore.getInstance("AndroidKeyStore"); store.load(null);
            if (store.containsAlias(ALIAS)) return (SecretKey) store.getKey(ALIAS, null);
            if (!create) throw new IllegalStateException("Key unavailable");
            KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            generator.init(new KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                    .setKeySize(256).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(true).setUserAuthenticationRequired(false).build());
            return generator.generateKey();
        }
    }

    private File path(String key) { return new File(directory, key + ".v1"); }
    private String lockId(String key) { return path(key).getAbsolutePath(); }
    private boolean exists(String key) {
        File file = path(key);
        return file.exists() || new File(file + ".bak").exists() || new File(file + ".new").exists();
    }
    private boolean anyEncrypted() { return exists("settings") || exists("sync_key") || exists("close_watch"); }

    private void block(String key) {
        BLOCKED.add(lockId(key)); status.put(key, "blocked");
        try { state.edit().putBoolean(key, true).commit(); } catch (Exception ignored) { }
    }

    private void unblock(String key) throws Exception {
        if (!state.edit().remove(key).commit()) throw new IllegalStateException("State unavailable");
        BLOCKED.remove(lockId(key));
    }

    private boolean blocked(String key) { return BLOCKED.contains(lockId(key)) || state.getBoolean(key, false); }

    private byte[] aad(String key) { return ("pro.dewiar.app/" + key + "/v1").getBytes(StandardCharsets.UTF_8); }

    private String seal(String key, String value) throws Exception {
        if (value == null || value.length() > MAX_BYTES) throw new IllegalArgumentException("Value too large");
        byte[] raw = value.getBytes(StandardCharsets.UTF_8);
        if (raw.length > MAX_BYTES) throw new IllegalArgumentException("Value too large");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        // Never regenerate a missing keystore key while any ciphertext still exists.
        cipher.init(Cipher.ENCRYPT_MODE, keys.get(!anyEncrypted()));
        cipher.updateAAD(aad(key));
        return "v1:" + Base64.encodeToString(cipher.getIV(), Base64.NO_WRAP) + ":"
                + Base64.encodeToString(cipher.doFinal(raw), Base64.NO_WRAP);
    }

    private String open(String key, String value) throws Exception {
        if (value == null || value.length() > MAX_ENVELOPE) throw new IllegalArgumentException("Invalid envelope");
        String[] parts = value.split(":", -1);
        if (parts.length != 3 || !"v1".equals(parts[0])) throw new IllegalArgumentException("Invalid envelope");
        byte[] iv = Base64.decode(parts[1], Base64.NO_WRAP), encrypted = Base64.decode(parts[2], Base64.NO_WRAP);
        if (iv.length != 12 || encrypted.length < 16 || encrypted.length > MAX_BYTES + 16) throw new IllegalArgumentException("Invalid envelope");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, keys.get(false), new GCMParameterSpec(128, iv));
        cipher.updateAAD(aad(key));
        return new String(cipher.doFinal(encrypted), StandardCharsets.UTF_8);
    }

    private String encrypted(String key) throws Exception {
        try (FileInputStream input = new AtomicFile(path(key)).openRead(); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[4096]; int n;
            while ((n = input.read(buffer)) != -1) {
                if (output.size() + n > MAX_ENVELOPE) throw new IllegalArgumentException("Invalid envelope");
                output.write(buffer, 0, n);
            }
            return new String(output.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    private void store(String key, String value) throws Exception {
        String sealed = seal(key, value);
        if (!value.equals(open(key, sealed))) throw new IllegalStateException("Encryption verification failed");
        if (!directory.isDirectory() && !directory.mkdirs()) throw new IllegalStateException("Storage unavailable");
        AtomicFile file = new AtomicFile(path(key)); FileOutputStream output = null;
        try {
            output = file.startWrite(); output.write(sealed.getBytes(StandardCharsets.UTF_8));
            output.flush(); output.getFD().sync();  // Surface fsync failure before AtomicFile's final rename.
            file.finishWrite(output); output = null;
            // Read the file afresh, not a SharedPreferences cache, before deleting legacy data.
            if (!sealed.equals(encrypted(key)) || !value.equals(open(key, encrypted(key)))) throw new IllegalStateException("Storage verification failed");
        } catch (Exception error) {
            if (output != null) file.failWrite(output);
            throw error;
        }
    }

    private void cleanup(String key) {
        boolean pending = state.getBoolean("cleanup." + key, false);
        boolean clean = (!legacy.contains(key) && !pending) || legacy.edit().remove(key).commit();
        // commit(false) may already change SharedPreferences' memory cache; retry the disk cleanup.
        if (clean) state.edit().remove("cleanup." + key).commit();
        else state.edit().putBoolean("cleanup." + key, true).commit();
        status.put(key, clean ? "encrypted" : "cleanup_pending");
    }

    String read(String key) {
        if (!protects(key)) throw new IllegalArgumentException("Unsupported protected preference");
        synchronized (LOCK) {
            try {
                String value;
                if (exists(key)) value = open(key, encrypted(key));
                else if (legacy.contains(key)) {
                    value = legacy.getString(key, ""); store(key, value);
                } else { unblock(key); status.put(key, "empty"); return ""; }
                unblock(key); cleanup(key);
                return value;
            } catch (Exception ignored) {
                block(key);
                // No exception cause: provider errors and values must not reach crash logs or JavaScript.
                throw new IllegalStateException("Protected preferences unavailable");
            }
        }
    }

    boolean write(String key, String value) {
        if (!protects(key)) return false;
        synchronized (LOCK) {
            try {
                if (blocked(key)) return false;
                if (exists(key)) open(key, encrypted(key));  // A corrupt old value is never replaced by default settings.
                store(key, value); cleanup(key); return true;
            } catch (Exception ignored) { block(key); return false; }
        }
    }

    // Отказ хранилища останавливает фоновые authenticated requests; legacy здесь не обходится.
    String background() {
        try { return read("close_watch"); } catch (Exception ignored) { return null; }
    }

    static String background(Context context) {
        try { return new SecurePrefs(context, context.getSharedPreferences("dewiar", Context.MODE_PRIVATE)).background(); }
        catch (Exception ignored) { return null; }
    }

    private String stateName(String key) {
        try { if (blocked(key)) return "blocked"; } catch (Exception ignored) { return "blocked"; }
        return status.containsKey(key) ? status.get(key) : "unchecked";
    }

    String status() {
        synchronized (LOCK) {
            return "{\"scheme\":\"AndroidKeyStore/AES-GCM\",\"settings\":\"" + stateName("settings")
                    + "\",\"sync_key\":\"" + stateName("sync_key") + "\",\"close_watch\":\"" + stateName("close_watch")
                    + "\",\"hardware_backed\":\"not_checked\",\"device_authentication_required\":false}";
        }
    }
}
