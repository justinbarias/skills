# .NET scaffold

Set the solution up so the compiler and analyzers catch mistakes before a reviewer has to. Put these files at the root of the .NET tree.

## `global.json`

Pins the SDK and selects the test runner. Replace the version with the installed .NET 10 SDK (`dotnet --version`). These files were built and tested on SDK 10.0.115.

```json
{
  "sdk": { "version": "10.0.100", "rollForward": "latestFeature" },
  "test": { "runner": "Microsoft.Testing.Platform" }
}
```

## `Directory.Build.props`

Applies to every project under it.

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>14.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <InvariantGlobalization>true</InvariantGlobalization>
  </PropertyGroup>
</Project>
```

`InvariantGlobalization` makes culture-sensitive calls behave the same on every machine. Leave it out if the product needs real culture data, and rely on the analyzer rules below.

## `Directory.Packages.props`

Holds every package version in one place. Project files then reference packages without a version.

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="xunit.v3.mtp-v2" Version="4.0.3" />
  </ItemGroup>
</Project>
```

## Test projects

With the Microsoft.Testing.Platform runner a test project is an executable. Each test project file looks like this. It turns the doc-comment check off, because the build settings above would otherwise fail every undocumented test method.

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <IsPackable>false</IsPackable>
    <GenerateDocumentationFile>false</GenerateDocumentationFile>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="xunit.v3.mtp-v2" />
    <Using Include="Xunit" />
    <ProjectReference Include="../../src/Name/Name.csproj" />
  </ItemGroup>
</Project>
```

Check NuGet for the current `xunit.v3.mtp-v2` version before pinning it. Inside `TheoryData` rows, write values as tuples. Collection expressions do not compile there.

## `.editorconfig`

Raise the rules that catch the Python-to-C# mistakes from the rulebook to errors.

```ini
root = true

[*.cs]
dotnet_diagnostic.CA1305.severity = error   # pass an IFormatProvider
dotnet_diagnostic.CA1307.severity = error   # pass a StringComparison
dotnet_diagnostic.CA1310.severity = error   # pass a StringComparison for correctness
dotnet_diagnostic.CA2016.severity = error   # forward the CancellationToken
dotnet_diagnostic.CA2007.severity = none    # ConfigureAwait is not needed in app code
dotnet_diagnostic.CS8600.severity = error   # null assigned to non-nullable
dotnet_diagnostic.CS8602.severity = error   # possible null dereference
dotnet_diagnostic.CS8604.severity = error   # possible null argument

[*.g.cs]
generated_code = true
```

The last block exempts generated files such as lookup tables from style rules.

Two analyzer rules affect how Python code can be shaped. CA1710 requires exception class names to end in `Exception`, so follow the exception naming rule in the rulebook. CA1810 rejects static constructors, so port code that runs on import as static field initialisers or an explicit startup call.

## Projects

Keep the layout close to the Python package so reviewers can find things.

| Project | Holds |
| --- | --- |
| `src/<Name>` | The ported package, one folder per Python subpackage |
| `src/<Name>.PyCompat` | Helpers for Python behaviour that C# lacks |
| `tests/<Name>.Tests` | Ported unit tests, same names as the pytest tests |
| `tests/<Name>.PyCompat.Tests` | Property tests for the helpers |

## The `PyCompat` library

Build only the helpers the code being ported needs, and test them before any other code. Implementers call them. They should not work out these semantics again at each call site.

| Helper | Matches Python |
| --- | --- |
| `FloorDiv(long a, long b)` | `a // b`, rounds toward negative infinity |
| `Mod(long a, long b)` | `a % b`, result takes the sign of `b` |
| `Len(string s)` | `len(s)` in code points |
| `Slice(string s, int? start, int? stop)` | `s[start:stop]` in code points, with negative indexes |
| `At(string s, int index)` | `s[index]` in code points, with negative indexes |
| `Truthy(...)` overloads | `bool(x)` for strings, numbers and collections, for the few places where the type is truly open |
| `Repr(...)` overloads | `repr(x)` and `str(x)` for floats and bools, where their text reaches output |
| `Lower`, `Upper`, `Title`, `Capitalize` | The `str` methods with full Unicode case mapping, when the source applies them to text that may be outside ASCII |
| Character class tests | `str.isalnum`, `isdigit`, `isspace` and the like, when the result reaches output |

There is no general regex helper. Translate each pattern by hand with the regex rules in the rulebook.

Generate a file of inputs and expected outputs from Python, including negative numbers, zero divisors, empty strings, emoji and combining marks, and check every helper against it.

## The agent's loop

Run these after every unit, in this order.

```bash
dotnet build -warnaserror
```

```bash
dotnet format --verify-no-changes
```

```bash
dotnet test
```

A single project builds in seconds, so the compiler belongs inside the per-unit loop.
