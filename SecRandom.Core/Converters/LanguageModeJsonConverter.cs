using System.Text.Json;
using System.Text.Json.Serialization;
using SecRandom.Core.Enums.Configs;

namespace SecRandom.Core.Converters;

// JsonStringEnumConverter ignores JsonPropertyName on enum members before .NET 10,
// so legacy settings with localized language names cannot deserialize on the net6
// port. This converter mirrors the member names explicitly.
public class LanguageModeJsonConverter : JsonConverter<LanguageMode>
{
    public override LanguageMode Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.Number)
        {
            var number = reader.GetInt32();
            if (Enum.IsDefined(typeof(LanguageMode), number))
                return (LanguageMode)number;
            throw new JsonException($"Unknown LanguageMode numeric value {number}.");
        }

        if (reader.TokenType != JsonTokenType.String)
            throw new JsonException($"Unexpected token {reader.TokenType} for LanguageMode.");

        var name = reader.GetString();
        foreach (var field in typeof(LanguageMode).GetFields().Where(field => field.IsStatic))
        {
            var attributeName = field.GetCustomAttributes(typeof(JsonPropertyNameAttribute), false)
                .OfType<JsonPropertyNameAttribute>()
                .FirstOrDefault()?.Name;
            if (string.Equals(name, attributeName, StringComparison.Ordinal) ||
                (options.PropertyNameCaseInsensitive &&
                 string.Equals(name, attributeName, StringComparison.OrdinalIgnoreCase)))
                return (LanguageMode)field.GetValue(null)!;
        }

        throw new JsonException($"Unknown LanguageMode value '{name}'.");
    }

    public override void Write(Utf8JsonWriter writer, LanguageMode value, JsonSerializerOptions options)
    {
        var field = typeof(LanguageMode).GetField(value.ToString());
        var attributeName = field?.GetCustomAttributes(typeof(JsonPropertyNameAttribute), false)
            .OfType<JsonPropertyNameAttribute>()
            .FirstOrDefault()?.Name;
        writer.WriteStringValue(attributeName ?? value.ToString());
    }
}
