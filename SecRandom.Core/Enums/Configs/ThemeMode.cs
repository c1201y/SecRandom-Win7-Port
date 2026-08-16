using System.Text.Json.Serialization;

namespace SecRandom.Core.Enums.Configs;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum ThemeMode
{
    [JsonPropertyName("LIGHT")] Light,

    [JsonPropertyName("DARK")] Dark,

    [JsonPropertyName("AUTO")] Auto
}