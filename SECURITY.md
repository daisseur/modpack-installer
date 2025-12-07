# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by creating a private security advisory on GitHub or by contacting the maintainers directly.

**Please do not create public issues for security vulnerabilities.**

## Security Considerations

### API Key
This project uses the CurseForge API which requires an API key. The key included in this project is:
- A publicly available project-specific key
- Rate-limited by the project
- Not a secret credential

**IMPORTANT**: If you fork or modify this project, you MUST obtain your own API key from CurseForge. See the [CurseForge API documentation](https://support.curseforge.com/en/support/solutions/articles/9000208346-about-the-curseforge-api-and-how-to-apply-for-a-key) for details.

### File Operations
The project performs several file operations that could be security-sensitive:
- Downloads files from CurseForge API
- Extracts zip files
- Creates symbolic links
- Modifies launcher profiles

All file operations are performed with user consent and within expected directories.

### Java Execution
The project includes a Java helper class (`ForgeHack.java`) that:
- Is compiled and executed locally
- Is open source and can be audited
- Assists with Forge modloader installation
- Requires JDK to be installed on the system

### Network Requests
The project makes network requests to:
- CurseForge API (api.curseforge.com)
- Minecraft Forge download servers (files.minecraftforge.net, maven.minecraftforge.net)
- Fabric Maven repository (maven.fabricmc.net)

All downloads are verified by the CurseForge API metadata.

## Best Practices

When using this tool:
1. Only download modpacks from trusted sources
2. Review the modpack contents before installation
3. Keep your Java installation up to date
4. Regularly run the cleanup script to remove unused mods
5. Use the latest version of this tool

## Known Limitations

- This tool is designed for Linux systems only
- It requires manual download for some mods due to CurseForge distribution policies
- The tool requires appropriate permissions to create directories and symbolic links
