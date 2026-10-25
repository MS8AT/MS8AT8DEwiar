package pro.dewiar.app;

import java.util.Locale;

/** ANDROID-001: один язык для слуха и голоса. Неизвестное значение — прежний русский. */
public final class Language {
    private Language() { }

    public static String code(String value) {
        if ("en".equals(value) || "zh-CN".equals(value)) return value;
        return "ru";
    }

    public static Locale locale(String value) {
        String c = code(value);
        return "en".equals(c) ? Locale.US : "zh-CN".equals(c) ? Locale.SIMPLIFIED_CHINESE : new Locale("ru", "RU");
    }

    public static String tag(String value) { return locale(value).toLanguageTag(); }
    public static String shortCode(String value) { return locale(value).getLanguage(); }
    public static boolean matches(String value, Locale voice) {
        return voice != null && shortCode(value).equals(voice.getLanguage());
    }

    // Android TTS: язык/страна/вариант доступны при >= 0; -1 — нет данных, -2 — не поддерживается.
    public static boolean available(int result) { return result >= 0; }
}
