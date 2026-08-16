using System.Text.RegularExpressions;

namespace SecRandom.Services.ImportExport;

internal static partial class DiagnosticTextRedactor
{
    public static string Redact(string text)
    {
        text = BearerTokenRegex.Replace(text, "Bearer <redacted>");
        text = SecretValueRegex.Replace(text, "$1<redacted>");
        text = AuthorizationRegex.Replace(text, "$1$2<redacted>");
        text = FilePathRegex.Replace(text, "<path>");
        return EmailRegex.Replace(text, "<email>");
    }

    private static readonly Regex BearerTokenRegex = new("(?i)\\bBearer\\s+[A-Za-z0-9._~+/-]+=*", RegexOptions.Compiled);
    private static readonly Regex SecretValueRegex = new("(?i)(\\\"?(?:password|secret|token)\\\"?\\s*[:=]\\s*)(\\\"[^\\\"]*\\\"|[^\\s,;}\\]]+)", RegexOptions.Compiled);
    private static readonly Regex AuthorizationRegex = new("(?i)(authorization\\s*[:=]\\s*)(\\\"?Bearer\\s+)?(\\\"[^\\\"]*\\\"|[^\\s,;}\\]]+)", RegexOptions.Compiled);
    private static readonly Regex FilePathRegex = new("[A-Za-z]:\\\\[^\\s\"]+|/[^\\s\"]+");
    private static readonly Regex EmailRegex = new("[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}", RegexOptions.IgnoreCase | RegexOptions.Compiled);
}
