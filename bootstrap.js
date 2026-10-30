/* eslint-env browser */
/* global Zotero */

/**
 * Attachment Type Icons
 *
 * Zotero decides an attachment's icon in Zotero.Item.prototype.getItemTypeIconName()
 * (chrome/content/zotero/xpcom/data/item.js). It recognises PDF, EPUB, image and video;
 * every other imported file falls through to "attachmentFile", which _item-tree.scss
 * maps to document.svg -- the blank page. So .docx, .xlsx and .pptx all render
 * identically, and Zotero also strips the extension from the attachment title, leaving
 * nothing to tell them apart by.
 *
 * This plugin wraps that one function to return a distinct name for Office, Markdown, XMind and HTML files, and
 * ships CSS defining icons for those names. The icons are Zotero's own attachment
 * geometry with a recoloured badge, so they sit flush with the native PDF/EPUB ones.
 *
 * Nothing else is touched: double-clicking still hands the file to the OS as before.
 */

var STYLE_ID = 'zotero-office-icons-stylesheet';
var XHTML_NS = 'http://www.w3.org/1999/xhtml';

var rootURI;

// Suffixes appended to "attachment". These must stay in step with FAMILIES in
// tools/gen-icons.py, which generates the matching selectors in style.css.
var BY_CONTENT_TYPE = {
	// Word
	'application/msword': 'Word',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.template': 'Word',
	'application/vnd.ms-word.document.macroenabled.12': 'Word',
	'application/vnd.ms-word.template.macroenabled.12': 'Word',
	'application/vnd.oasis.opendocument.text': 'Word',
	'application/rtf': 'Word',
	'text/rtf': 'Word',
	// Excel
	'application/vnd.ms-excel': 'Excel',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.template': 'Excel',
	'application/vnd.ms-excel.sheet.macroenabled.12': 'Excel',
	'application/vnd.ms-excel.sheet.binary.macroenabled.12': 'Excel',
	'application/vnd.oasis.opendocument.spreadsheet': 'Excel',
	'text/csv': 'Excel',
	// PowerPoint
	'application/vnd.ms-powerpoint': 'PowerPoint',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
	'application/vnd.openxmlformats-officedocument.presentationml.slideshow': 'PowerPoint',
	'application/vnd.openxmlformats-officedocument.presentationml.template': 'PowerPoint',
	'application/vnd.ms-powerpoint.presentation.macroenabled.12': 'PowerPoint',
	'application/vnd.ms-powerpoint.slideshow.macroenabled.12': 'PowerPoint',
	'application/vnd.oasis.opendocument.presentation': 'PowerPoint',
	// Markdown
	'text/markdown': 'Markdown',
	'text/x-markdown': 'Markdown',
	// XMind
	'application/vnd.xmind.workbook': 'XMind',
	'application/x-xmind': 'XMind',
	// HTML
	'text/html': 'HTML',
	'application/xhtml+xml': 'HTML',
};

// Fallback for files Zotero stored with no content type, or with a generic one such as
// application/octet-stream -- common for files added by drag-and-drop or by a sync tool.
var BY_EXTENSION = {
	doc: 'Word', docx: 'Word', docm: 'Word', dot: 'Word', dotx: 'Word', dotm: 'Word',
	odt: 'Word', rtf: 'Word',
	xls: 'Excel', xlsx: 'Excel', xlsm: 'Excel', xlsb: 'Excel', xlt: 'Excel',
	xltx: 'Excel', xltm: 'Excel', ods: 'Excel', csv: 'Excel',
	ppt: 'PowerPoint', pptx: 'PowerPoint', pptm: 'PowerPoint', pps: 'PowerPoint',
	ppsx: 'PowerPoint', ppsm: 'PowerPoint', pot: 'PowerPoint', potx: 'PowerPoint',
	odp: 'PowerPoint',
	md: 'Markdown', markdown: 'Markdown', mdown: 'Markdown', mkd: 'Markdown',
	mkdn: 'Markdown', mdwn: 'Markdown', mdtxt: 'Markdown', mdtext: 'Markdown',
	xmind: 'XMind', xmt: 'XMind',
	html: 'HTML', htm: 'HTML',
};

/**
 * @param {Zotero.Item} item - a file attachment
 * @return {String|null} "Word" | "Excel" | "PowerPoint" | "Markdown" | "XMind" | "HTML", or null otherwise
 */
function familyFor(item) {
	let contentType = item.attachmentContentType;
	if (contentType) {
		let family = BY_CONTENT_TYPE[contentType.toLowerCase()];
		if (family) {
			return family;
		}
	}

	let name = null;
	try {
		name = item.attachmentFilename || item.attachmentPath;
	}
	catch (e) {
		// Some link modes have no path; fall through
	}
	if (!name) {
		return null;
	}

	let match = /\.([A-Za-z0-9]+)$/.exec(name);
	return match ? BY_EXTENSION[match[1].toLowerCase()] || null : null;
}

function patchIconName() {
	let original = Zotero.Item.prototype.getItemTypeIconName;
	if (original.officeIconsWrapper) {
		return;
	}

	let wrapper = function (skipLinkMode = false) {
		try {
			if (this.isFileAttachment()) {
				let family = familyFor(this);
				if (family) {
					let linked = this.attachmentLinkMode === Zotero.Attachments.LINK_MODE_LINKED_FILE;
					return 'attachment' + family + (!skipLinkMode && linked ? 'Link' : '');
				}
			}
		}
		catch (e) {
			// Never let an icon lookup break a row render
			Zotero.logError(e);
		}
		return original.apply(this, arguments);
	};

	wrapper.officeIconsWrapper = true;
	wrapper.officeIconsOriginal = original;
	Zotero.Item.prototype.getItemTypeIconName = wrapper;
}

function unpatchIconName() {
	let current = Zotero.Item.prototype.getItemTypeIconName;
	if (current && current.officeIconsWrapper) {
		Zotero.Item.prototype.getItemTypeIconName = current.officeIconsOriginal;
	}
}

function addStyle(win) {
	let doc = win.document;
	if (doc.getElementById(STYLE_ID)) {
		return;
	}
	let link = doc.createElementNS(XHTML_NS, 'link');
	link.id = STYLE_ID;
	link.rel = 'stylesheet';
	link.href = rootURI + 'style.css';
	doc.documentElement.appendChild(link);
}

function removeStyle(win) {
	win.document.getElementById(STYLE_ID)?.remove();
}

/** Repaint rows that were rendered before the patch landed (or after it was removed). */
function redraw(win) {
	try {
		win.ZoteroPane?.itemsView?.tree?.invalidate();
	}
	catch (e) {
		Zotero.logError(e);
	}
}

function install() {}

function startup({ rootURI: uri }) {
	rootURI = uri;
	patchIconName();
	// onMainWindowLoad only fires for windows opened from now on
	for (let win of Zotero.getMainWindows()) {
		addStyle(win);
		redraw(win);
	}
}

function onMainWindowLoad({ window: win }) {
	addStyle(win);
}

function onMainWindowUnload({ window: win }) {
	removeStyle(win);
}

function shutdown() {
	unpatchIconName();
	for (let win of Zotero.getMainWindows()) {
		removeStyle(win);
		redraw(win);
	}
	rootURI = undefined;
}

function uninstall() {}
