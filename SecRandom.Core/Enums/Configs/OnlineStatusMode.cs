using System.Text.Json.Serialization;

namespace SecRandom.Core.Enums.Configs;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum OnlineStatusMode
{
    [JsonPropertyName("full")] Full,

    [JsonPropertyName("anonymous")]
    Anonymous,

    [JsonPropertyName("off")] Off
}
