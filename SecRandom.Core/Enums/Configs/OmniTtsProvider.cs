using System.Text.Json.Serialization;

namespace SecRandom.Core.Enums.Configs;

// net6 port: alpha2 marks members with JsonStringEnumMemberName (net10 only). The
// default JsonStringEnumConverter matches member names case-insensitively, so
// legacy "OpenAI" values still bind to OpenAi.
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum OmniTtsProvider
{
    OpenAi,

    FishAudio,

    MiMo,

    Gemini,

    Custom
}
