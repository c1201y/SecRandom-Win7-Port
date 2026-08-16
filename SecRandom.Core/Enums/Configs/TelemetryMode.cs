using System.Text.Json.Serialization;

namespace SecRandom.Core.Enums.Configs;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum TelemetryMode
{
    [JsonPropertyName("full")] Full,

    [JsonPropertyName("anonymous")]
    Anonymous,

    [JsonPropertyName("off")] Off
}