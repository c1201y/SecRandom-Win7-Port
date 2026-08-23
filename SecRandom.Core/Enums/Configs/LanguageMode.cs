using System.Text.Json.Serialization;
using SecRandom.Core.Converters;

namespace SecRandom.Core.Enums.Configs;

[JsonConverter(typeof(LanguageModeJsonConverter))]
public enum LanguageMode
{
    [JsonPropertyName("简体中文")] ChineseSimplified,

    [JsonPropertyName("English")] English,

    [JsonPropertyName("日本語")] Japanese
}