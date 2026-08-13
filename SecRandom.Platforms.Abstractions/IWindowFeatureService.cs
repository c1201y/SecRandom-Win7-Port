namespace SecRandom.Platforms.Abstractions;

public interface IWindowFeatureService
{
    WindowFeatures SupportedFeatures { get; }

    WindowFeatureApplyResult Apply(PlatformWindowHandle window, WindowFeatureRequest request);

    /// <summary>
    /// Applies a whole-window opacity through native window styles. Values outside 0..1 are clamped.
    /// This is distinct from the application-level rendering opacity and works where the
    /// transparency level hint is unavailable (for example layered windows on older Windows).
    /// </summary>
    WindowFeatureApplyResult ApplyOpacity(PlatformWindowHandle window, double opacity);
}
