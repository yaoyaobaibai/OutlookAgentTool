// Keyboard shortcuts support
function C1KeyboardShortcutsClass()
{
	this.shortcuts = [];
	document.onkeydown = this.keydown;
}
C1KeyboardShortcutsClass.prototype.keydown = function(event)
{
	if (typeof(event) == 'undefined')
		event = window.event;
	if (window.C1KeyboardShortcuts.processKeyEvent(event.keyCode, event.ctrlKey, event.altKey, event.shiftKey))
		c1c_stopEvent(event);
}
C1KeyboardShortcutsClass.prototype.addShortcut = function(linkItem, shortcutText)
{
	var shortcutObj = this.parse(shortcutText);
	if (shortcutObj)
		this.add(linkItem, shortcutObj);
}
C1KeyboardShortcutsClass.prototype.add = function(linkItem, shortcutObj)
{
	this.shortcuts[this.shortcuts.length] = {item:linkItem, shortcut:shortcutObj};
}
C1KeyboardShortcutsClass.prototype.processKeyEvent = function(keyCode, ctrlKey, altKey, shiftKey)
{
	for(var i=0;i<this.shortcuts.length;i++)
	{
		if (this.equal(this.shortcuts[i].shortcut, keyCode, ctrlKey, altKey, shiftKey))
		{
			if (this.checkItemExists(this.shortcuts[i].item))
			{
			    c1c_focus(this.shortcuts[i].item._boundary);
				c1c_item_onclick(this.shortcuts[i].item, null, true);
				return true;
			}
		}
	}
	return false;
}
C1KeyboardShortcutsClass.prototype.checkItemExists = function(item)
{
	return document.getElementById(item.id) == item.Item;
}
C1KeyboardShortcutsClass.prototype.parse = function(shortcutText)
{
	var res = {keyCode:0, keyCodeAlt:0, ctrlKey:false, altKey:false, shiftKey: false};
	var parts = shortcutText.split('+');
	for(var i=0;i<parts.length;i++)
	{
		var literal = parts[i].toLowerCase();
		if (literal == 'ctrl')
		{
			res.ctrlKey = true;
		}
		else if (literal == 'alt')
		{
			res.altKey = true;
		}
		else if (literal == 'shift')
		{
			res.shiftKey = true;
		}
		else 
		{
			if (literal.length == 1 && ((literal >= 'a' && literal <= 'z') || (literal >= '0' && literal <= '9')))
			{
				res.keyCode = literal.charCodeAt(0);
				res.keyCodeAlt = literal.toUpperCase().charCodeAt(0);
			}
			else if ((literal.length == 2 || literal.length == 3) && literal.charAt(0) == 'f')
			{
				var num = literal.substring(1);
				num = parseInt(num);
				if (!isNaN(num) && num >= 1 && num <= 12)
					res.keyCode = 111+num;
			}
			else if (literal.length == 4 && literal.indexOf('num') == 0)
			{
				var num = literal.charCodeAt(3) + 48;
				if (!num >= 96 && num <= 105)
					res.keyCode = num;
			}
			else if (literal == 'enter')
				res.keyCode = 13;
			else if (literal == 'backspace')
				res.keyCode = 8;
			else if (literal == 'ins')
				res.keyCode = 45;
			else if (literal == 'del')
				res.keyCode = 46;
			else if (literal == 'home')
				res.keyCode = 36;
			else if (literal == 'end')
				res.keyCode = 35;
			else if (literal == 'pgup')
				res.keyCode = 33;
			else if (literal == 'pgdn')
				res.keyCode = 34;
			else if (literal == 'space')
				res.keyCode = 32;
		}
	}
	if (res.keyCode)
		return res;
	return null;
}
C1KeyboardShortcutsClass.prototype.equal = function(src, keyCode, ctrlKey, altKey, shiftKey)
{
	return (keyCode != 0 && (src.keyCode == keyCode || src.keyCodeAlt == keyCode) && src.ctrlKey == ctrlKey && src.altKey == altKey && src.shiftKey == shiftKey); 
}
window.C1KeyboardShortcuts = new C1KeyboardShortcutsClass();
