// Paste into Zotero: Tools -> Developer -> Run JavaScript, then Run.
// Reports exactly why the .xpi is refused, and installs it if nothing blocks it.

var { AddonManager } = ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs");

// Set this to the absolute path of the .xpi that build.sh produced.
var path = "/path/to/attachment-type-icons-1.0.2.xpi";
var out = [];

if (path.startsWith("/path/to/")) {
	return "Edit `path` at the top of this script to point at your .xpi first.";
}

out.push("app        = " + Services.appinfo.version + "  (ID " + Services.appinfo.ID + ")");
out.push("signatures required = " + Services.prefs.getBoolPref("xpinstall.signatures.required", true));
out.push("strictCompatibility = " + AddonManager.strictCompatibility);
out.push("");

// Zotero's Run JavaScript wraps this in an async function when that box is
// ticked, so the value must be returned explicitly.
var existing = await AddonManager.getAddonByID("office-icons@linqingming.local");
if (existing) {
	out.push("ALREADY INSTALLED: v" + existing.version
		+ "  active=" + existing.isActive
		+ "  userDisabled=" + existing.userDisabled
		+ "  appDisabled=" + existing.appDisabled);
	return out.join("\n");
}

var install = await AddonManager.getInstallForFile(Zotero.File.pathToFile(path));

if (!install) {
	out.push("getInstallForFile returned null");
}
else {
	let name = Object.keys(AddonManager)
		.filter(k => k.startsWith("ERROR_") && AddonManager[k] === install.error)
		.join(", ") || "(no error)";
	out.push("install.error = " + install.error + "   " + name);
	out.push("install.state = " + install.state);
	out.push("install.name  = " + install.name);

	if (install.addon) {
		let a = install.addon;
		out.push("addon.id        = " + a.id);
		out.push("addon.version   = " + a.version);
		out.push("isCompatible    = " + a.isCompatible);
		out.push("appDisabled     = " + a.appDisabled);
		out.push("signedState     = " + a.signedState);
		out.push("blocklistState  = " + a.blocklistState);
	}
	else {
		out.push("addon = null  (manifest failed to load)");
	}

	if (!install.error) {
		out.push("");
		out.push("--- no blocking error, attempting install ---");
		try {
			await install.install();
			out.push("RESULT: OK, state = " + install.state);
		}
		catch (e) {
			out.push("RESULT: install() threw: " + e);
			out.push("install.error is now " + install.error);
		}
	}
}

return out.join("\n");
