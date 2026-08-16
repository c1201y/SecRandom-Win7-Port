using System.Text.Json.Serialization;

namespace SecRandom.Core.Enums.Configs;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum LanguageMode
{
    [JsonPropertyName("简体中文")] ChineseSimplified,

    [JsonPropertyName("English")] English,

    [JsonPropertyName("日本語")] Japanese
}