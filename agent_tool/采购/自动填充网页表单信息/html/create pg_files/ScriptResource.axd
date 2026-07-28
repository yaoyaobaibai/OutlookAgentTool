// Fix problem of IE6 BackgroundImage flickering
/*@cc_on
@if (@_win32)
  document.execCommand("BackgroundImageCache",false,true);
@end
@*/


var c1c_submenu_zindex = 32000;
var c1_MenuTracker = new C1MenuTracker();
var c1_TreeViewTracker = new C1TreeViewTracker();
var c1c_submenu_offset_left = 0;
var c1c_submenu_offset_right = 8;
var __c1_designTime = (document.getElementById('__c1_designTime') != null);
window.c1c_next_focus_element = null;

var c1c_nav_IE = false;
if (window.opera) {
  c1c_nav_IE = false;
}
else if (document.all && navigator.userAgent.toLowerCase().indexOf('msie')!=-1) {
  c1c_nav_IE = true;
}

function c1c_force_ie_layout(style)
{
  if(c1c_nav_IE && typeof(style.zoom) != 'undefined')
  {
    // ie7
    if(style.zoom == "" || style.zoom == "normal")
      style.zoom = "1";
    else if(style.zoom == "1")
      style.zoom = "";
  }
}

function c1c_focus(el)
{
  // I can not directly call el.focus() because of a FireFox focus issue
  c1c_next_focus_element =   el;
  el.tabIndex = 2;
  setTimeout('window.c1c_next_focus_element.focus()', 10);
}
document.expando = true;

function c1c_init_control(id)
{
  var item = c1c_getElementById(id);
  var control = new C1WebCommandBase();
  control._control = item;
  item._proxy = control;
  return control;
}

function c1c_init_item(controlId, userClick, userSelect, userMouseDown, userMouseEnter, userMouseLeave, userMouseMove, userMouseOut, userMouseOver, userMouseUp, userMouseWheel, itemStyle, mouseOverItemStyle, selectedItemStyle, mouseOverSelectedItemStyle, navigateUrl, target, enabled, selected, handleClick, handleSelect, allowSelect, postBackFunc, itemBackImageUrl, itemImageUrl, itemLeftBorderImageUrl, itemRightBorderImageUrl, mouseOverBackImageUrl, mouseOverImageUrl, mouseOverLeftBorderImageUrl, mouseOverRightBorderImageUrl, selectedBackImageUrl, selectedImageUrl, selectedLeftBorderImageUrl, selectedRightBorderImageUrl, mouseOverSelectedBackImageUrl, mouseOverSelectedImageUrl, mouseOverSelectedLeftBorderImageUrl, mouseOverSelectedRightBorderImageUrl, causesValidation, indicatorUrl, mouseOverIndicatorUrl, selectedIndicatorUrl, mouseOverSelectedIndicatorUrl)
{
  var htmlItem = c1c_getElementById(controlId);
  var item = new LinkItem(htmlItem);
  item.UserOnClick = userClick;
  item.UserOnSelect = userSelect;
  item.UserOnMouseDown = userMouseDown;
  item.UserOnMouseEnter = userMouseEnter;
  item.UserOnMouseLeave = userMouseLeave;
  item.UserOnMouseMove = userMouseMove;
  item.UserOnMouseOut = userMouseOut;
  item.UserOnMouseOver = userMouseOver;
  item.UserOnMouseUp = userMouseUp;
  item.UserOnMouseWheel = userMouseWheel;
  item.ItemStyle = itemStyle;
  item.MouseOverItemStyle = mouseOverItemStyle;
  item.SelectedItemStyle = selectedItemStyle;
  item.MouseOverSelectedItemStyle = mouseOverSelectedItemStyle;
  item.BackImageUrl = itemBackImageUrl;
  item.ImageUrl = itemImageUrl;
  item.LeftBorderImageUrl = itemLeftBorderImageUrl;
  item.RightBorderImageUrl = itemRightBorderImageUrl;
  item.MouseOverBackImageUrl = mouseOverBackImageUrl;
  item.MouseOverImageUrl = mouseOverImageUrl;
  item.MouseOverLeftBorderImageUrl = mouseOverLeftBorderImageUrl;
  item.MouseOverRightBorderImageUrl = mouseOverRightBorderImageUrl;
  item.SelectedBackImageUrl = selectedBackImageUrl;
  item.SelectedImageUrl = selectedImageUrl;
  item.SelectedLeftBorderImageUrl = selectedLeftBorderImageUrl;
  item.SelectedRightBorderImageUrl = selectedRightBorderImageUrl;
  item.MouseOverSelectedBackImageUrl = mouseOverSelectedBackImageUrl;
  item.MouseOverSelectedImageUrl = mouseOverSelectedImageUrl;
  item.MouseOverSelectedLeftBorderImageUrl = mouseOverSelectedLeftBorderImageUrl;
  item.MouseOverSelectedRightBorderImageUrl = mouseOverSelectedRightBorderImageUrl;
  if (indicatorUrl)
    item.IndicatorUrl = indicatorUrl;
  if (selectedIndicatorUrl)
    item.SelectedIndicatorUrl = selectedIndicatorUrl;
  if (mouseOverIndicatorUrl)
    item.MouseOverIndicatorUrl = mouseOverIndicatorUrl;
  if (mouseOverSelectedIndicatorUrl)
    item.MouseOverSelectedIndicatorUrl = mouseOverSelectedIndicatorUrl;
  item.Enabled = enabled;
  item.CausesValidation = causesValidation;
  item.Selected = selected;
  item.NavigateUrl = navigateUrl;
  item.Target = target;
  item.RaisePostBackOnClick = handleClick;
  item.RaisePostBackOnSelect = handleSelect;
  item.AllowSelect = allowSelect;

  item.PostBackFunction = postBackFunc;
  item.Index = 0;
  item.PrepareImage();
  if (item.Enabled)
    item.InitFreez();
  if (selected)
    item._appliedStyle = selectedItemStyle;
  else
    item._appliedStyle = itemStyle;
  return item;
}

function LinkItem(item, _designTime)
{
  this.Item = item;
  item._proxy = this;
  this._boundary = c1c_getElementById(item.id+"_bt");
  this.id = item.id;
  this.UserOnClick = null;
  this.UserOnSelect = null;
  this.UserOnMouseDown = null;
  this.UserOnMouseEnter = null;
  this.UserOnMouseLeave = null;
  this.UserOnMouseMove = null;
  this.UserOnMouseOut = null;
  this.UserOnMouseOver = null;
  this.UserOnMouseUp = null;
  this.UserOnMouseWheel = null;
  this.ItemStyle = null;
  this.MouseOverItemStyle = null;
  this.SelectedItemStyle = null;
  this.MouseOverSelectedItemStyle = null;
  this.BackImageUrl = null;
  this.ImageUrl = null;
  this.LeftBorderImageUrl = null;
  this.RightBorderImageUrl = null;
  this.MouseOverBackImageUrl = null;
  this.MouseOverImageUrl = null;
  this.MouseOverLeftBorderImageUrl = null;
  this.MouseOverRightBorderImageUrl = null;
  this.SelectedBackImageUrl = null;
  this.SelectedImageUrl = null;
  this.SelectedLeftBorderImageUrl = null;
  this.SelectedRightBorderImageUrl = null;
  this.MouseOverSelectedBackImageUrl = null;
  this.MouseOverSelectedImageUrl = null;
  this.MouseOverSelectedLeftBorderImageUrl = null;
  this.MouseOverSelectedRightBorderImageUrl = null;
  this.IndicatorUrl = "";
  this.SelectedIndicatorUrl = "";
  this.MouseOverIndicatorUrl = "";
  this.MouseOverSelectedIndicatorUrl = "";

  this._setImageUrl = "";
  this._setBackImageUrl = "";
  this._setLeftBorderImageUrl = "";
  this._setRightBorderImageUrl = "";
  this.Enabled = true;
  this.CausesValidation = false;
  this.Selected = false;
  this.NavigateUrl = "";
  this.Target = "";
  this.RaisePostBackOnClick = false;
  this.RaisePostBackOnSelect = false;
  this.AllowSelect = false;
  this.PostBackFunction = null;
  this._appliedStyle = "";
  this.RootControl  = null;
  this.OwnerGroup = null;
  this.CancelClick = false;
  this.CancelSelect = false;
  this._isHeader = false;
  this._linkedGroupBodyElement = null;
  this._linkedGroupElement = null;
  this._linkedGroupElementHeight = "";
  this._collapseIndicatorElement = null;
  this._trackingSubmenu = false;
  this.ChildGroup = null;
  this._image = null;
  this._mouseover = false;

  this._needFreezText = false;
  this._freezBoundaryWidth = "";
  this._freezBoundaryWidthMouseOver = "";
  this._freezBoundaryWidthSelected = "";
  this._freezBoundaryWidthSelectedMouseOver = "";

  this._el_mbc = null;
  this._el_lbi = null;
  this._el_rbi = null;
  this._el_img = null;
  this._el_ind = null;
  this._el_cbx = null;
  this.getInnerElements();

  this.CallbackFunction = null;
  this.Populated = true;
  this.CallbackWaitControlID = "";
  this.OnClick = function (event) 
  { 
    c1c_item_onclick(item._proxy, event);
  }
  this.OnSelect = function (event) 
  { 
    c1c_item_onselect(item._proxy, event);
  }
  this.OnMouseDown = function (event) 
  { 
    c1c_item_onmousedown(item._proxy, event);
  }
  this.OnMouseEnter = function (event) 
  { 
    c1c_item_onmouseenter(item._proxy, event);
  }
  this.OnMouseLeave = function (event) 
  { 
    c1c_item_onmouseleave(item._proxy, event);
  }
  this.OnMouseMove = function (event) 
  { 
    c1c_item_onmousemove(item._proxy, event);
  }
  this.OnMouseOut = function (event) 
  { 
    if (typeof(event) == 'undefined')
      event = window.event;
    var src = null;
    if (event.srcElement)
      src = event.srcElement;
    else if (event.target)
      src = event.target;
    var tgt;
    if (event.relatedTarget)
      tgt = event.relatedTarget;
    else if (event.toElement)
      tgt = event.toElement;

    if (!c1c_object_contains(item._proxy._boundary, tgt))
    {
      this._mouseover = false;
      c1c_item_onmouseout(item._proxy, event);
      c1_MenuTracker.ItemOut(item._proxy);
    }
  }
  this.OnMouseOver = function (event) 
  { 
    if (!this._mouseover)
    {
      this._mouseover = true;
      c1c_item_onmouseover(item._proxy, event);
      c1_MenuTracker.ItemIn(item._proxy);
    }
  }
  this.OnMouseUp = function (event) 
  { 
    c1c_item_onmouseup(item._proxy, event);
  }
  this.OnMouseWheel = function (event) 
  { 
    c1c_item_onmousewheel(item._proxy, event);
  }
  this.OnFocus =  function (event) 
  { 
    c1c_item_onfocus(item._proxy, event);
  }
  this.OnBlur = function (event) 
  { 
    c1c_item_onblur(item._proxy, event);
  }
  this.OnKeyUp =  function (event) 
  { 
    c1c_item_onkeyup(item._proxy, event);
  }
  c1c_attach_event(this._boundary, this.OnClick, "click");
  c1c_attach_event(this._boundary, this.OnMouseDown, "mousedown");
  c1c_attach_event(this._boundary, this.OnMouseEnter, "mouseenter");
  c1c_attach_event(this._boundary, this.OnMouseLeave, "mouseleave");
  c1c_attach_event(this._boundary, this.OnMouseMove, "mousemove");
  c1c_attach_event(this._boundary, this.OnMouseOut, "mouseout");
  c1c_attach_event(this._boundary, this.OnMouseOver, "mouseover");
  c1c_attach_event(this._boundary, this.OnMouseUp, "mouseup");
  c1c_attach_event(this._boundary, this.OnMouseWheel, "mousewheel");
  c1c_attach_event(this._boundary, this.OnFocus, "focus");
}

LinkItem.prototype.findTheFirstItemInChildGroup = function()
{
}
LinkItem.prototype.downKey = function(event)
{
  if (this.RootControl._isToolBar && !this.RootControl.horizontal)
    this.toolBarFocusNext();
  else if (this.RootControl._isTabStrip)
    this.tabStripFocusNextItem();
  else if (this.RootControl._isTopicBar)
    this.topicBarFocusNext();
  else if (this.RootControl._isTreeView)
    this.treeFocusDown();
  // Menu
  if (this.RootControl._isMenu && this.IsHorizontal() && this.HasSubMenu())
  {
    // If ClickToOpen
    if (!this.RootControl._menuOpened)
    {
      this.RootControl.OpenMenu();
      c1c_item_onmouseover(this);
    }
    // Find Next Item 
    var enItem = null;
    for(var i=0; i<this.ChildGroup.Items.length; i++)
    {
      if (this.ChildGroup.Items[i].Enabled)
      {
        enItem = this.ChildGroup.Items[i];
        break;
      }
    }
    // Move focus to the next item
    if (enItem)
    {
      this.RootControl._nextKeySubmenu = this.ChildGroup;
      this.ChildGroup.OnMouseOver();
      c1c_focus(enItem._boundary);
    }

  } 
  else
    if (this.RootControl._isMenu && !this.IsHorizontal())
    {
      // Find Next Item 
      var enItem = null;
      var fl = false;
      for(var i=0; i<this.OwnerGroup.Items.length; i++)
      {
        if (fl && this.OwnerGroup.Items[i].Enabled)
        {
          enItem = this.OwnerGroup.Items[i];
          break;
        }
        if (!fl && this.OwnerGroup.Items[i] == this)
          fl = true;
      }
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = this.OwnerGroup;
        c1c_focus(enItem._boundary);
      }

    }
}
LinkItem.prototype.upKey = function(event)
{
  if (this.RootControl._isToolBar && !this.RootControl.horizontal)
    this.toolBarFocusPrev();
  else if (this.RootControl._isTabStrip)
    this.tabStripFocusPrevItem();
  else if (this.RootControl._isTopicBar)
    this.topicBarFocusPrev();
  else if (this.RootControl._isTreeView)
    this.treeFocusUp();
  // Menu
  if (this.RootControl._isMenu && this.IsHorizontal())
  {
    // If ClickToOpen
    if (this.RootControl._menuOpened)
    {
      this.RootControl.CloseMenu();
      this.HideSubMenu();
    }
  }
  else
    // Menu
    // Vertical
    if (this.RootControl._isMenu && !this.IsHorizontal())
    {
      // Find Next Item 
      var enItem = null;
      var fl = false;
      for(var i=this.OwnerGroup.Items.length-1; i>=0; i--)
      {
        if (fl && this.OwnerGroup.Items[i].Enabled)
        {
          enItem = this.OwnerGroup.Items[i];
          break;
        }
        if (!fl && this.OwnerGroup.Items[i] == this)
          fl = true;
      }
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = this.OwnerGroup;
        c1c_focus(enItem._boundary);
      }
      else if (this.OwnerGroup._parentItem)
      {
        this.RootControl._nextKeySubmenu = this.OwnerGroup._parentItem.OwnerGroup;
        this.OwnerGroup.OnMouseOut();
        c1c_focus(this.OwnerGroup._parentItem._boundary);
      }
    }
}
LinkItem.prototype.rightKey = function(event)
{
  if (this.RootControl._isToolBar && this.RootControl.horizontal)
    this.toolBarFocusNext();
  else if (this.RootControl._isTabStrip)
    this.tabStripFocusNextHeader();
  else if (this.RootControl._isTreeView)
    this.treeFocusRight();
  // Menu
  else if (this.IsHorizontal())
  {
    // Find Next Item 
    var enItem = null;
    var fl = false;
    for(var i=0; i<this.OwnerGroup.Items.length; i++)
    {
      if (fl && this.OwnerGroup.Items[i].Enabled)
      {
        enItem = this.OwnerGroup.Items[i];
        break;
      }
      if (!fl && this.OwnerGroup.Items[i] == this)
        fl = true;
    }
    // Move focus to the next item
    if (enItem)
    {
      this.RootControl._nextKeySubmenu = this.OwnerGroup;
      c1c_focus(enItem._boundary);
    }
  } 
  else
    if (this.RootControl._isMenu && !this.IsHorizontal() && this.HasSubMenu())
    {
      // If ClickToOpen
      if (!this.RootControl._menuOpened)
      {
        this.RootControl.OpenMenu();
        c1c_item_onmouseover(this);
      }

      var enItem = null;
      for(var i=0; i<this.ChildGroup.Items.length; i++)
      {
        if (this.ChildGroup.Items[i].Enabled)
        {
          enItem = this.ChildGroup.Items[i];
          break;
        }
      }
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = this.ChildGroup;
        this.ChildGroup.OnMouseOver();
        c1c_focus(enItem._boundary);
      }
    }
    else if (this.RootControl._isMenu && !this.IsHorizontal() && this.RootControl._horizontalMenu)
    {
      var enItem = null;
      var fl = false;
      for(var i=0; i<this.RootControl.Items.length; i++)
      {
        if (fl && this.RootControl.Items[i].Enabled)
        {
          enItem = this.RootControl.Items[i];
          break;
        }
        if (!fl && this.RootControl.Items[i].ChildGroup.Visible())
          fl = true;
      }
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = enItem.OwnerGroup;
        c1c_focus(enItem._boundary);
      }
    }

}
LinkItem.prototype.leftKey = function(event)
{
  if (this.RootControl._isToolBar && this.RootControl.horizontal)
    this.toolBarFocusPrev();
  else if (this.RootControl._isTabStrip)
    this.tabStripFocusPrevHeader();
  else if (this.RootControl._isTreeView)
    this.treeFocusLeft(event);
  // Menu
  if (this.RootControl._isMenu && !this.IsHorizontal() && this.IsRootMenuItem() && this.ChildGroup)
  {
    // If ClickToOpen
    if (this.RootControl._menuOpened)
    {
      this.RootControl.CloseMenu();
      this.HideSubMenu();
    }
  }
  if (this.RootControl._isMenu && this.IsHorizontal())
  {
    // Find Next Item 
    var enItem = null;
    var fl = false;
    for(var i=this.OwnerGroup.Items.length-1; i>=0; i--)
    {
      if (fl && this.OwnerGroup.Items[i].Enabled)
      {
        enItem = this.OwnerGroup.Items[i];
        break;
      }
      if (!fl && this.OwnerGroup.Items[i] == this)
        fl = true;
    }
    // Move focus to the next item
    if (enItem)
    {
      this.RootControl._nextKeySubmenu = this.OwnerGroup;
      c1c_focus(enItem._boundary);
    }

  } 
  else
    if (this.RootControl._isMenu && !this.IsHorizontal() && this.OwnerGroup._parentItem && !this.OwnerGroup._parentItem.OwnerGroup._horizontalMenu)
    {
      var enItem = this.OwnerGroup._parentItem;
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = this.ChildGroup;
        enItem.ChildGroup.OnMouseOut();
        c1c_focus(enItem._boundary);
      }
    }
    else if (this.RootControl._isMenu && !this.IsHorizontal() && this.RootControl._horizontalMenu)
    {
      var enItem = null;
      var fl = false;
      for(var i=this.RootControl.Items.length-1; i>=0; i--)
      {
        if (fl && this.RootControl.Items[i].Enabled)
        {
          enItem = this.RootControl.Items[i];
          break;
        }
        if (!fl && this.RootControl.Items[i].ChildGroup.Visible())
          fl = true;
      }
      // Move focus to the next item
      if (enItem)
      {
        this.RootControl._nextKeySubmenu = enItem.OwnerGroup;
        c1c_focus(enItem._boundary);
      }
    }

}
LinkItem.prototype.toolBarFocusNext = function()
{
  // Find Next Group
  var enItem = null;
  var enGroup = null;
  var fl = false;
  for(var i=0; i<this.OwnerGroup.Items.length; i++)
  {
    if (fl && this.OwnerGroup.Items[i].Enabled)
    {
      enItem = this.OwnerGroup.Items[i];
      break;
    }
    if (!fl && this.OwnerGroup.Items[i] == this)
      fl = true;
  }
  fl = false;
  if (!enItem)
    for(var i=0; i<this.RootControl.Groups.length; i++)
    {
      if (fl)
      {
        enGroup = this.RootControl.Groups[i];
        for(var g=0; g<enGroup.Items.length; g++)
        {
          if (fl && enGroup.Items[g].Enabled)
          {
            enItem = enGroup.Items[g];
            break;
          }
        }
      }
      if (!fl && this.RootControl.Groups[i] == this.OwnerGroup)
        fl = true;
    }
  if (enItem)
  {
    this.RootControl._nextKeySubmenu = this.OwnerGroup;
    c1c_focus(enItem._boundary);
  }

}
LinkItem.prototype.toolBarFocusPrev = function()
{
  // Find Next Group
  var enItem = null;
  var enGroup = null;
  var fl = false;
  for(var i=this.OwnerGroup.Items.length-1; i>=0; i--)
  {
    if (fl && this.OwnerGroup.Items[i].Enabled)
    {
      enItem = this.OwnerGroup.Items[i];
      break;
    }
    if (!fl && this.OwnerGroup.Items[i] == this)
      fl = true;
  }
  fl = false;
  if (!enItem)
    for(var i=this.RootControl.Groups.length-1; i>=0; i--)
    {
      if (fl)
      {
        enGroup = this.RootControl.Groups[i];
        for(var g=enGroup.Items.length-1; g>=0; g--)
        {
          if (fl && enGroup.Items[g].Enabled)
          {
            enItem = enGroup.Items[g];
            break;
          }
        }
      }
      if (!fl && this.RootControl.Groups[i] == this.OwnerGroup)
        fl = true;
    }
  if (enItem)
  {
    this.RootControl._nextKeySubmenu = this.OwnerGroup;
    c1c_focus(enItem._boundary);
  }

}
LinkItem.prototype.topicBarFocusNext = function()
{
  var enItem = null;
  var enGroup = null;
  if ((this._isHeader && !this.Selected && this.Index < this.OwnerGroup.Items.length - 1)
      || (this._isHeader && this.Selected && this.Index < this.OwnerGroup.Items.length - 1 && this.RootControl.Groups[this.Index].Items.length == 0))
  {
    enItem = this.OwnerGroup.Items[this.Index + 1]
         // Find Next Header
         c1c_focus(enItem._boundary);
    return;
  }
  else if (this._isHeader && this.Selected && this.RootControl.Groups[this.Index].Items.length > 0)
  {
    enItem = this.RootControl.Groups[this.Index].Items[0];
    // Find Next Header
    c1c_focus(enItem._boundary);
    return;
  }
  else if (!this._isHeader && this.Index < this.OwnerGroup.Items.length - 1)
  {
    enItem = this.OwnerGroup.Items[this.Index+1];
    // Find Next Header
    c1c_focus(enItem._boundary);
    return;
  }
  else if (!this._isHeader && this.Index == this.OwnerGroup.Items.length - 1)
  {
    enItem = this.RootControl._headersGroup.Items[this.OwnerGroup.Index+1];
    // Find Next Header
    if (enItem)
      c1c_focus(enItem._boundary);
    return;
  }

}
LinkItem.prototype.topicBarFocusPrev = function()
{
  var enItem = null;
  var enGroup = null;
  if (!this._isHeader && this.Index > 0)
  {
    enItem = this.OwnerGroup.Items[this.Index - 1]
         // Find Next Header
         c1c_focus(enItem._boundary);
    return;
  }
  else if (!this._isHeader && this.Index == 0)
  {
    enItem = this.RootControl._headersGroup.Items[this.OwnerGroup.Index];
    // Find Next Header
    c1c_focus(enItem._boundary);
    return;
  }
  else if (this._isHeader && this.Index > 0 && this.RootControl._headersGroup.Items[this.Index-1].Selected && this.RootControl.Groups[this.Index-1].Items.length > 0)
  {
    enItem = this.RootControl.Groups[this.Index-1].Items[this.RootControl.Groups[this.Index-1].Items.length-1];
    // Find Next Header
    c1c_focus(enItem._boundary);
    return;
  }
  else if (this._isHeader && this.Index > 0)
  {
    enItem = this.RootControl._headersGroup.Items[this.Index-1];
    // Find Next Header
    c1c_focus(enItem._boundary);
    return;
  }

}
LinkItem.prototype.tabStripFocusNextItem = function()
{
  var enItem = null;
  if (this._isHeader && this.RootControl.Groups[this.Index].Items.length > 0)
  {
    enItem = this.RootControl.Groups[this.Index].Items[0];
    c1c_focus(enItem._boundary);
    return;
  }      
  else if (!this._isHeader && this.OwnerGroup.Items.length-1 > this.Index)
  {
    enItem = this.OwnerGroup.Items[this.Index+1];
    c1c_focus(enItem._boundary);
    return;
  }
}
LinkItem.prototype.tabStripFocusPrevItem = function()
{
  var enItem = null;
  if (!this._isHeader && this.Index == 0)
  {
    enItem = this.RootControl._headersGroup.Items[this.OwnerGroup.Index];
    c1c_focus(enItem._boundary);
    return;
  }      
  else if (!this._isHeader)
  {
    enItem = this.OwnerGroup.Items[this.Index-1];
    c1c_focus(enItem._boundary);
    return;
  }
}
LinkItem.prototype.tabStripFocusNextHeader = function()
{
  var enItem = null;
  if (this._isHeader && this.RootControl._headersGroup.Items.length-1 > this.Index)
  {
    enItem = this.RootControl._headersGroup.Items[this.Index+1];
    c1c_focus(enItem._boundary);
    return;
  }      
}
LinkItem.prototype.tabStripFocusPrevHeader = function()
{
  var enItem = null;
  if (this._isHeader && this.Index > 0)
  {
    enItem = this.RootControl._headersGroup.Items[this.Index-1];
    c1c_focus(enItem._boundary);
    return;
  }      
}
LinkItem.prototype.treeFocusRight = function(event)
{
  var enItem = null;
  if (this.ChildGroup && this.ChildGroup.Visible() && this.ChildGroup.Items.length > 0)
  {
    enItem = this.ChildGroup.Items[0];
    c1c_focus(enItem._boundary);
    return;
  }      
  else if (this.ChildGroup && !this.ChildGroup.Visible())
  {
    SetPlusMinusClicked();
    this.OnClick(event);
    return;
  }      
}
LinkItem.prototype.treeFocusLeft = function(event)
{
  var enItem = null;
  if (this.ChildGroup && this.ChildGroup.Visible())
  {
    SetPlusMinusClicked();
    this.OnClick(event);
    return;
  }      
  else if (this.OwnerGroup._parentItem)
  {
    enItem = this.OwnerGroup._parentItem;
    c1c_focus(enItem._boundary);
    return;
  }      
}
LinkItem.prototype.treeFocusDown = function(event)
{
  var enItem = null;
  if (this.ChildGroup && this.ChildGroup.Visible() && this.ChildGroup.Items.length > 0)
  {
    enItem = this.ChildGroup.Items[0];
    c1c_focus(enItem._boundary);
    return;
  }      
  else 
  {
    var el;
    el = this;
    do
    {
      if (el.OwnerGroup.Items.length-1 > el.Index)
      {
        enItem = el.OwnerGroup.Items[el.Index+1];
        c1c_focus(enItem._boundary);
        return;
      }
      el = el.OwnerGroup._parentItem;
    }
    while (el);
  }      
}
LinkItem.prototype.treeFocusUp = function(event)
{
  var enItem = null;
  if (this.Index > 0)
  {
    enItem  = this.OwnerGroup.Items[this.Index-1];
    while (enItem.ChildGroup && enItem.ChildGroup.Visible() && enItem.ChildGroup.Items.length > 0)
    {
      enItem = enItem.ChildGroup.Items[enItem.ChildGroup.Items.length-1];
    }
    c1c_focus(enItem._boundary);
    return;
  }      
  else if (this.OwnerGroup._parentItem)
  {
    enItem = this.OwnerGroup._parentItem;
    c1c_focus(enItem._boundary);
    return;
  }      
}
LinkItem.prototype.SetFreezWidth = function(mouseover)
{
  if (!this._el_mbc)
    this._el_mbc = document.getElementById(this.id + "_mbc");
  var el = this._el_mbc;
  var w = "";
  if (el)
  {
    if (mouseover)
    {
      if (this.Selected)
        w = this._freezBoundaryWidthSelectedMouseOver;
      else
        w = this._freezBoundaryWidthMouseOver;
    } else {
      if (this.Selected)
        w = this._freezBoundaryWidthSelected;
      else
        w = this._freezBoundaryWidth;
    }
    el.style.padding = w;      
  }
}
LinkItem.prototype.GetBorderWidth = function(style)
{
  var ss = style.split(";");
  for (var i = 0; i < ss.length; i++)
  {
    var pair = c1c_splitTwice(ss[i], ":");

    if (pair.length == 2 && pair[0] == "borderStyle" && pair[1] == "none")
      return "";
    else if (pair.length == 2 && pair[0] == "borderWidth")
    {
      if (pair[1] == "0px" || pair[1] == "0%")
        return "";
      else
        return pair[1];
    }
  }
  return "";
}
LinkItem.prototype.SetLabelPaddings = function(left, top, right, bottom)
{
  if (this.Item)
  {
    var inTable = this.Item.firstChild;
    if (inTable)
    {
      inTable.rows[1].cells[1].style.paddingLeft = left;
      inTable.rows[1].cells[1].style.paddingTop = top;
      inTable.rows[1].cells[1].style.paddingRight = right;
      inTable.rows[1].cells[1].style.paddingBottom = bottom;
    }
  }
}
LinkItem.prototype.InitFreez = function()
{
  var bw0 = this.GetBorderWidth(this.ItemStyle);
  var bw1 = this.GetBorderWidth(this.MouseOverItemStyle);
  var bw2 = this.GetBorderWidth(this.SelectedItemStyle);
  var bw3 = this.GetBorderWidth(this.MouseOverSelectedItemStyle);
  var w = "";
  if (bw0 == bw1 && bw1 == bw2 && bw2 == bw3)
    return;
  if (bw0 != "" && bw1 != "" && bw2 != "" && bw3 != "")
    return;
  if (bw0 != "")
    w = bw0;
  else if (bw1 != "")
    w = bw1;
  else if (bw2 != "")
    w = bw2;
  else if (bw3 != "")
    w = bw3;
  if (bw0 == "")
    this._freezBoundaryWidth = w; 
  if (bw1 == "")
    this._freezBoundaryWidthMouseOver = w;
  if (bw2 == "")
    this._freezBoundaryWidthSelected = w;
  if (bw3 == "")
    this._freezBoundaryWidthSelectedMouseOver = w;
  this.SetFreezWidth(false);
}
LinkItem.prototype.AddGroup = function(group)
{
  this.ChildGroup = group;
  this.ChildGroup.RootControl = this.RootControl;
  this.ChildGroup._parentItem = this;
  c1c_AllGroups.Add(group);
}
LinkItem.prototype.getInnerElements = function()
{
  if (!this._el_mbc)
    this._el_mbc = c1c_getElementById(this.Item.id + "_mbc");
  if (!this._el_img)
    this._el_img = c1c_getElementById(this.Item.id + "_img");
  if (!this._el_lbi)
    this._el_lbi = c1c_getElementById(this.Item.id + "_lbi");
  if (!this._el_rbi)
    this._el_rbi = c1c_getElementById(this.Item.id + "_rbi");
  if (!this._el_ind)
    this._el_ind = c1c_getElementById(this.Item.id + "_ind");
}

LinkItem.prototype.Refresh = function() {
  c1c_item_endhover(this);
  this.RefreshLinkedGroup();
}
LinkItem.prototype.RefreshLinkedGroup = function() {
  if (this.RaisePostBackOnClick)
    return;
  if (this._linkedGroupBodyElement) {
    if (!this._linkedGroupBodyElement.parentElement)
      this._linkedGroupBodyElement = document.getElementById(this._linkedGroupBodyElement.id);      

    if (typeof(this.c1visible) == 'undefined')
    {
      this.c1visible = (this._linkedGroupBodyElement.style.display == "none") ? false : true;
      this._groupBodyElementEffect = document.getElementById(this._linkedGroupBodyElement.id+'_expand');
    }
    if (this.Selected && !this.c1visible)
    {
      var expEl = this._groupBodyElementEffect;
      if (expEl)
      {
        expEl.style.display = 'none';
        if (this.effect)
          this.effect.cancel();
        if (this.RootControl.ExpandEffect == "Slide")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.SlideDown(expEl, options);
        }
        else if (this.RootControl.ExpandEffect == "Blind")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.BlindDown(expEl, options);
        }
        else if (this.RootControl.ExpandEffect == "Fade")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.Appear(expEl, options);
        }
        else
        {
          expEl.style.visibility = "";
          expEl.style.display = "";
        }
      }
      this.c1visible = true;
      this._linkedGroupBodyElement.style.display = "";
      if (this._linkedGroupElement)
        this._linkedGroupElement.style.height = this._linkedGroupElementHeight;
      if (this.RootControl._isTabStrip)   
      {
        if (this.RootControl._control.style.width == "100%")
        {
            // Fixes #17587. Workaround.
            this.RootControl._control.style.width = "99%";
            this.RootControl._control.style.width = "100%";  
        }
      }
    }
    else if (!this.Selected && this.c1visible)
    {
      var expEl = this._groupBodyElementEffect;
      if (expEl)
      {
        if (this.effect)
          this.effect.cancel();
        if (this.RootControl.ExpandEffect == "Slide")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.SlideUp(expEl, options);
        }
        else if (this.RootControl.ExpandEffect == "Blind")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.BlindUp(expEl, options);
        }
        else if (this.RootControl.ExpandEffect == "Fade")
        {
          var options = {};
          options.duration = this.RootControl.ExpandEffectDuration / 1000; 
          this.effect = new Effect.Fade(expEl, options);
        }
        else
        {
          expEl.style.display = "none";
        }
      }
      this.c1visible = false;
      this._linkedGroupBodyElement.style.display = "none";
      if (this._linkedGroupElement)
        this._linkedGroupElement.style.height = "";
    }
  }
}
LinkItem.prototype.HoverMenuItem = function() {
  if (this.IsMenu() && this.HasSubMenu() && this.CheckClickToOpen())
    this.ShowSubMenu();
}
LinkItem.prototype.EndHoverMenuItem = function() {
}
LinkItem.prototype.IsMenu = function() {
  return this.RootControl._isMenu;
}
LinkItem.prototype.HasSubMenu = function() {
  if (this.ChildGroup)
    return true;
  else
    return false;
}
LinkItem.prototype.CheckClickToOpen = function() {
  return !this.RootControl._clickToOpen || this.RootControl._menuOpened;
}
LinkItem.prototype.ShowSubMenu = function() {
  this.ChildGroup.ShowSubMenu();
}
LinkItem.prototype.HideSubMenu = function() {
  this.ChildGroup.HideSubMenu();
}
LinkItem.prototype.IsHorizontal = function() {
  if (this.OwnerGroup == this.RootControl && this.RootControl._horizontalMenu)
    return true;
  else
    return false;
}
LinkItem.prototype.RefreshCheckbox = function() {
  if (!this._el_cbx)
    this._el_cbx = document.getElementById(this.Item.id+"_cbx");
  var cbx = this._el_cbx;
  if (cbx && cbx.checked != this.Selected)
    cbx.checked = this.Selected;
}
LinkItem.prototype.InitMenu = function() {
  if (this.HasSubMenu())
    this.ChildGroup.InitMenu();
}
LinkItem.prototype.OnShowSubmenu = function () {
  this._trackingSubmenu = true;
  this.Refresh();
}
LinkItem.prototype.OnHideSubmenu = function () {
  this._trackingSubmenu = false;
  this.Refresh();
}
LinkItem.prototype.InHierarchy = function(submenu)  {
  if (this.HasSubMenu())
    return this.ChildGroup.InHierarchy(submenu);
  return false;
}
LinkItem.prototype.IsRootMenuItem = function() {
  return this.OwnerGroup == this.RootControl;
}
LinkItem.prototype.InitTreeItem = function(id, collapsed, expanded) {
  this._collapseIndicatorElement = c1c_getElementById(id);
  this._collapsedImgUrl = collapsed;
  this._expandedImgUrl = expanded;
}
LinkItem.prototype.InitTreeItemCallback = function(callbackProc, callbackWaitControlID)
{
  this.CallbackFunction = callbackProc;
  this.Populated = false;
  this.CallbackWaitControlID = callbackWaitControlID;
}
LinkItem.prototype.OnShowTreeGroup = function() {
  if (this._collapseIndicatorElement.tagName == "SPAN")
    this._collapseIndicatorElement.innerText = "-";
  else
    this._collapseIndicatorElement.src = this._expandedImgUrl;
}
LinkItem.prototype.OnHideTreeGroup = function() {
  if (this._collapseIndicatorElement.tagName == "SPAN")
    this._collapseIndicatorElement.innerText = "+";
  else
    this._collapseIndicatorElement.src = this._collapsedImgUrl;
}
LinkItem.prototype.PrepareImage = function() {
  if (!this._image) 
    this._image = c1c_getElementById(this.Item.id + "_img");
  if (!this._ind) 
    this._ind = c1c_getElementById(this.Item.id + "_ind");
  if (this._image && this._image.style.display == "none")
  {
    var imgsrc;
    if (this.Selected)
    {
      imgsrc = this.MouseOverSelectedImageUrl;
      if (imgsrc == '')
        imgsrc = this.ImageUrl;
      if (imgsrc == '')
        imgsrc = this.MouseOverImageUrl;
    } else {
      imgsrc = this.MouseOverImageUrl;
      if (imgsrc == '')
        imgsrc = this.SelectedImageUrl;
      if (imgsrc == '')
        imgsrc = this.MouseOverSelectedImageUrl;
    }
    if (imgsrc != '') {
      this._image.style.display = "none";
      //this._image.onload = function() { this.style.display='';};
      this._image.src = imgsrc;
    }
  }  
}
LinkItem.prototype.SetImageUrl = function(url, img) {
  if (img)     
  {
    if (url == '')
    {
      img.style.display = "none";
    }
    else
    {
      if (img.src != url)
        img.src = url;
      if (img.style.display != "")
        img.style.display = '';
    }
  }
}
LinkItem.prototype.SetTabStripSeparatorImageUrl = function(url) {
}
LinkItem.prototype.SetBackImageUrl = function(url, cell) {
  var newUrl;
  if (url && url != "")
    newUrl = "url("+url+")";
  else
    newUrl = "none";

  if (cell && cell.style.backgroundImage != newUrl)
  {
    cell.style.backgroundImage = newUrl;
  }
}
LinkItem.prototype.NextIsActive = function() {
  var gr = this.OwnerGroup;
  if (this.Index < (gr._count - 1) && gr.Items[this.Index+1].Selected)
    return true;
  else
    return false;
}
LinkItem.prototype.PerformPreloadImages = function() {
  if (this.BackImageUrl != "")
  {
    var img1 = new Image();
    img1.src = this.BackImageUrl;
  }
  if (this.ImageUrl != "")
  {
    var img2 = new Image();
    img2.src = this.ImageUrl;
  }
  if (this.MouseOverBackImageUrl != "")
  {
    var img3 = new Image();
    img3.src = this.MouseOverBackImageUrl;
  }
  if (this.MouseOverImageUrl != "")
  {
    var img4 = new Image();
    img4.src = this.MouseOverImageUrl;
  }
  if (this.SelectedBackImageUrl != "")
  {
    var img5 = new Image();
    img5.src = this.SelectedBackImageUrl;
  }
  if (this.SelectedImageUrl != "")
  {
    var img6 = new Image();
    img6.src = this.SelectedImageUrl;
  }
  if (this.MouseOverSelectedBackImageUrl != "")
  {
    var img7 = new Image();
    img7.src = this.MouseOverSelectedBackImageUrl;
  }
  if (this.MouseOverSelectedImageUrl != "")
  {
    var img8 = new Image();
    img8.src = this.MouseOverSelectedImageUrl;
  }
  if (this.LeftBorderImageUrl != "")
  {
    var img9 = new Image();
    img9.src = this.LeftBorderImageUrl;
  }
  if (this.RightBorderImageUrl != "")
  {
    var img10 = new Image();
    img10.src = this.RightBorderImageUrl;
  }
  if (this.MouseOverLeftBorderImageUrl != "")
  {
    var img11 = new Image();
    img11.src = this.MouseOverLeftBorderImageUrl;
  }
  if (this.MouseOverRightBorderImageUrl != "")
  {
    var img12 = new Image();
    img12.src = this.MouseOverRightBorderImageUrl;
  }
  if (this.SelectedLeftBorderImageUrl != "")
  {
    var img13 = new Image();
    img13.src = this.SelectedLeftBorderImageUrl;
  }
  if (this.SelectedRightBorderImageUrl != "")
  {
    var img14 = new Image();
    img14.src = this.SelectedRightBorderImageUrl;
  }
  if (this.MouseOverSelectedLeftBorderImageUrl != "")
  {
    var img15 = new Image();
    img15.src = this.MouseOverSelectedLeftBorderImageUrl;
  }
  if (this.MouseOverSelectedLeftBorderImageUrl != "")
  {
    var img16 = new Image();
    img16.src = this.MouseOverSelectedLeftBorderImageUrl;
  }
  if (this.IndicatorUrl != "")
  {
    var img17 = new Image();
    img17.src = this.IndicatorUrl;
  }
  if (this.MouseOverIndicatorUrl != "")
  {
    var img18 = new Image();
    img18.src = this.MouseOverIndicatorUrl;
  }
  if (this.SelectedIndicatorUrl != "")
  {
    var img19 = new Image();
    img19.src = this.SelectedIndicatorUrl;
  }
  if (this.MouseOverSelectedIndicatorUrl != "")
  {
    var img20 = new Image();
    img20.src = this.MouseOverSelectedIndicatorUrl;
  }
}

function c1c_get_group(id)
{
  var control = c1c_getElementById(id);
  var group = c1c_AllGroups.Get(id);
  if (control)
    control._proxy = group;
  return group;
}

function c1c_init_group(controlID, enabled, active, allowSelectItem, allowMultipleSelect, alwaysHasSelected, allowMultipleSelectInControl, allowUnselectItem, itemCount, selectedStatusFieldId)
{
  var control = c1c_getElementById(controlID);
  var group = new CustomGroup(itemCount, control);
  group.ControlID = controlID;
  group.Enabled = enabled;
  group.Index = 0;
  group.Active = active;
  group.AllowSelectItem = allowSelectItem;
  group.AllowMultipleSelect = allowMultipleSelect;
  group.AlwaysHasSelected = alwaysHasSelected;
  group.AllowMultipleSelectInControl = allowMultipleSelectInControl;
  group.AllowUnselectItem = allowUnselectItem;
  group.SelectedStatusField = c1c_getElementById(selectedStatusFieldId);
  return group;
}

function CustomGroup(ItemCount, control)
{
  this.ControlID = "";
  this.RootControl = null;
  this.Enabled = true;
  this.Index = 0;
  this.Active = true;
  this.AllowSelectItem = false;
  this.AllowMultipleSelect = false;
  this.AlwaysHasSelected = false;
  this.AllowMultipleSelectInControl = true;
  this.AllowUnselectItem = true;
  this.SelectedStatusField = null;
  this.Items = [];
  this._count = 0;
  this._groupBodyElement = null;
  this._parentItem = null;
  if (control)
    control._proxy = this;
  this._control = control;
  this.OffsetX = 0;
  this.OffsetY = 0;
  this.Opacity = 0;
  this.ShadowColor = "";
  this.ShadowDirection = 135;
  this.BackIframe = null;
  this.OnMouseOut = function (event)  { 
    c1_MenuTracker.SubmenuOut(control._proxy);
  }
  this.OnMouseOver = function(event) {
    c1_MenuTracker.SubmenuIn(control._proxy);
  }
}
CustomGroup.prototype.EnsureBackIframe = function() {
  if (!c1c_nav_IE || document.readyState != 'complete')
    return;
  if (!this.BackIframe)
  {
    this.BackIframe = document.createElement("iframe");
    this.BackIframe.src = "javascript:false;"     
                this.BackIframe.style.position = "absolute";
    this.BackIframe.style.filter = "progid:DXImageTransform.Microsoft.Alpha(style=0,opacity=0)";
    this.BackIframe.marginWidth = 0;
    this.BackIframe.marginHeight = 0;
    this.BackIframe.noresize = true;
    this.BackIframe.frameBorder = "no";
    this.BackIframe.scrolling = "no";
    this.BackIframe.style.zIndex = parseInt(this._groupBodyElement.style.zIndex) - 1;
    //  
    //document.body.appendChild(this.BackIframe);
    var par = c1c_getParentElement(this._groupBodyElement)
    par.appendChild(this.BackIframe);

  }
  this.BackIframe.style.display = this._groupBodyElement.style.display;
  this.BackIframe.style.visibility = this._groupBodyElement.style.visibility;   
  this.BackIframe.style.left = this._groupBodyElement.style.left;   
  this.BackIframe.style.top = this._groupBodyElement.style.top;
  this.BackIframe.width = this._groupBodyElement.offsetWidth + "px";
  this.BackIframe.height = this._groupBodyElement.offsetHeight + "px";

}
CustomGroup.prototype.AddItem = function  (item) {
  this.Items[this._count] = item;
  item.OwnerGroup = this;
  item.RootControl = this.RootControl;
  item.Index = this._count;
  this._count++;
  if (item.RootControl.PreloadImages)
    item.PerformPreloadImages();
}
CustomGroup.prototype._IsSingleSelected = function(item)
{
  for (var i=0; i<this._count; i++)
  {
    if (this.Items[i].Selected && this.Items[i] != item)
      return false;
  }
  return true;
}
CustomGroup.prototype.Select  = function (item, event) {
  var oldstate = item.Selected;
  if (this.AllowSelectItem)
  {
    var _allowUnselect = this.AllowUnselectItem && (!this.AlwaysHasSelected || !this._IsSingleSelected(item));
    item.CancelSelect = false;
    if (item.UserOnSelect && (!item.Selected || _allowUnselect)) 
    {
      item.Selected = true;
      item.UserOnSelect(item, event);
    }
    if (item.CancelSelect)
      return;
    if (_allowUnselect)
      item.Selected = !oldstate;
    else
      item.Selected = true;
    if (!this.AllowMultipleSelectInControl)
    {
      this.RootControl.ResetExceptingOne(item);
      if (this.RootControl._isTreeView || this.RootControl._isMenu)
        this.RootControl.RefreshSelectedItemsStatusField()
      else  
        this.RootControl.RefreshSelectedStatusFields();
    } 
    else if (!this.AllowMultipleSelect)
    {
      this.ResetExceptingOne(item);
      this.RefreshSelectedStatusField();
    } 
    else
      this.RefreshSelectedStatusField();
    if (this.RootControl._mixedMode)
      for (var i=0; i<this._count; i++)
      {
        this.Items[i].Refresh();
      }
    else
      item.Refresh();
  }
  if (!oldstate && item.Selected && item.RaisePostBackOnSelect && item.PostBackFunction)
    item.PostBackFunction()     
}
this.ResetAll = function () {
  this.ResetExceptingOne(null);
}
CustomGroup.prototype.ResetExceptingOne = function (item) {
  for (var i=0; i<this._count; i++)
  {
    if (this.Items[i] != item && item.Selected)
    {
      this.Items[i].Selected = false;
      this.Items[i].Refresh();
    }
  }
}
CustomGroup.prototype.RefreshSelectedStatusField  = function() {
  var s = "-1";
  for (var i=0; i<this._count; i++)
  {
    if (this.Items[i].Selected)
    {
      if (s != "")
        s += ";";
      s += i.toString();
    }
  }
  if (this.SelectedStatusField)
  {
    this.SelectedStatusField.value = s;
  }
}
CustomGroup.prototype.ShowSubMenu = function() {
  if (this._groupBodyElement  && (!this.effect || (this.effect && this.effect.state == "finished")) ) {
    if (typeof(this._groupBodyElement.c1visible) == 'undefined')
    {

      this._groupBodyElement.c1visible = (this._groupBodyElement.style.display != "none" && this._groupBodyElement.style.visibility != "hidden") ? true : false;
      this._groupBodyElementEffect = document.getElementById(this._groupBodyElement.id+'_expand');
      if (!this._groupBodyElementEffect)
        this._groupBodyElementEffect = this._groupBodyElement;
    }
    if (!this._groupBodyElement.c1visible)
    {
      var parZindex = c1c_submenu_zindex;
      if (!this._parentItem.IsRootMenuItem())
        parZindex = parseInt(this._parentItem.OwnerGroup._groupBodyElement.style.zIndex);
      var currZindex = parZindex + 1;

      var expEl = this._groupBodyElementEffect;
      if (expEl && this._groupBodyElement.style.position == "absolute" && expEl != this._groupBodyElement)
      {
        expEl.style.position = "absolute";
        expEl.style.display = 'none';

        this._groupBodyElement.style.position = "";
        this._groupBodyElement.style.display = "";
      }

      if (expEl.style.zIndex != currZindex)
        expEl.style.zIndex = currZindex;
      var left = c1c_getsubmenu_x(this, expEl) + this.OffsetX;
      var top = c1c_getsubmenu_y(this, expEl) + this.OffsetY;
      expEl.style.left = left + "px";
      expEl.style.top = top + "px";
      if (this.effect)
        this.effect.cancel();
      if (this.RootControl.ExpandEffect == "Slide")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.SlideDown(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Blind")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.BlindDown(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Fade")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.Appear(expEl, options);
        //this.EnsureBackIframe();
      }
      else
      {
        expEl.style.visibility = "";
        expEl.style.display = "";
        this.EnsureBackIframe();
      }
      this._groupBodyElement.c1visible = true;
    }
  }
  this._parentItem.OnShowSubmenu();
  c1_MenuTracker.OnShowSubmenu(this);
}
CustomGroup.prototype.HideSubMenu = function() {
  if (this._groupBodyElement  && (!this.effect || (this.effect && this.effect.state == "finished")) ) {
    if (typeof(this._groupBodyElement.c1visible) == 'undefined')
      this._groupBodyElement.c1visible = (this._groupBodyElement.style.display != "none" && this._groupBodyElement.style.visibility != "hidden") ? true : false;
    if (this._groupBodyElement.c1visible)
    {
      var expEl = this._groupBodyElementEffect;
      this._groupBodyElement.c1visible = false;
      if (this.effect)
        this.effect.cancel();
      if (this.RootControl.ExpandEffect == "Slide")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.SlideUp(expEl.id, options);
      }
      else if (this.RootControl.ExpandEffect == "Blind")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.BlindUp(expEl.id, options);
      }
      else if (this.RootControl.ExpandEffect == "Fade")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.Fade(expEl.id, options);
        //this.EnsureBackIframe();
      }
      else
      {
        expEl.style.display = "none";
        this.EnsureBackIframe();
      }
    }
  }
  this._parentItem.OnHideSubmenu();
  this._parentItem._trackingSubmenu = false;
  this.RootControl.onHideSubmenu(this);
}
CustomGroup.prototype.ShowTreeGroup = function(waitControl) {
  if (this._groupBodyElement  && (!this.effect || (this.effect && this.effect.state == "finished")) ) {
    if (typeof(this._groupBodyElement.c1visible) == 'undefined')
    {

      this._groupBodyElement.c1visible = (this._groupBodyElement.style.display != "none" && this._groupBodyElement.style.visibility != "hidden") ? true : false;
      this._groupBodyElementEffect = document.getElementById(this._groupBodyElement.id+'_expand');
      if (!this._groupBodyElementEffect)
        this._groupBodyElementEffect = this._groupBodyElement;
    }
    if (!this._groupBodyElement.c1visible)
    {
      var expEl = this._groupBodyElementEffect;
      if (expEl && this._groupBodyElement.style.display == "none" && expEl != this._groupBodyElement)
      {
        expEl.style.display = 'none';
        this._groupBodyElement.style.display = "";
      }
      if (this.effect)
        this.effect.cancel();
      if (this.RootControl.ExpandEffect == "Slide")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.SlideDown(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Blind")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.BlindDown(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Fade")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.Appear(expEl, options);
      }
      else
      {
        expEl.style.visibility = "";
        expEl.style.display = "";
      }
      this.OnShowTreeGroup();
      this._groupBodyElement.c1visible = true;
    }
    if (waitControl)
      c1c_append(this._groupBodyElement, waitControl);
  }
}
CustomGroup.prototype.HideTreeGroup = function(dontraise) {
  if (this._groupBodyElement && (!this.effect || (this.effect && this.effect.state == "finished")) ) {
    if (typeof(this._groupBodyElement.c1visible) == 'undefined')
    {

      this._groupBodyElement.c1visible = (this._groupBodyElement.style.display != "none" && this._groupBodyElement.style.visibility != "hidden") ? true : false;
      this._groupBodyElementEffect = document.getElementById(this._groupBodyElement.id+'_expand');
      if (!this._groupBodyElementEffect)
        this._groupBodyElementEffect = this._groupBodyElement;
    }
    if (this._groupBodyElement.c1visible)
    {
      var expEl = this._groupBodyElementEffect;
      if (this.effect)
        this.effect.cancel();
      if (this.RootControl.ExpandEffect == "Slide")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.SlideUp(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Blind")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.BlindUp(expEl, options);
      }
      else if (this.RootControl.ExpandEffect == "Fade")
      {
        var options = {};
        options.duration = this.RootControl.ExpandEffectDuration / 1000; 
        this.effect = new Effect.Fade(expEl, options);
      }
      else
      {
        expEl.style.display = "none";
      }
      this._groupBodyElement.c1visible = false;
      this.OnHideTreeGroup(dontraise);
    }
  }
}
CustomGroup.prototype.OnShowTreeGroup = function() {
  this._parentItem.OnShowTreeGroup();
  if (!__c1_designTime)
    this.RootControl._treeSelectedStatusField.value = this.RootControl._treeSelectedStatusField.value + this._control.id + "+;"
}
CustomGroup.prototype.OnHideTreeGroup = function(dontraise) {
  this._parentItem.OnHideTreeGroup();
  if (!dontraise && !__c1_designTime)
    this.RootControl._treeSelectedStatusField.value = this.RootControl._treeSelectedStatusField.value + this._control.id + "-;"
}
CustomGroup.prototype.Visible = function() {
  if (typeof(this._groupBodyElement.c1visible) == 'undefined')
  {

    this._groupBodyElement.c1visible = (this._groupBodyElement.style.display != "none" && this._groupBodyElement.style.visibility != "hidden") ? true : false;
    this._groupBodyElementEffect = document.getElementById(this._groupBodyElement.id+'_expand');
    if (!this._groupBodyElementEffect)
      this._groupBodyElementEffect = this._groupBodyElement;
  }
  return (this._groupBodyElement.c1visible);
}
CustomGroup.prototype.InitSubMenu = function(id, offsetX, offsetY, opacity, shadowColor, shadowDirection) {
  this._groupBodyElement = c1c_getElementById(id);
  this._groupBodyElement._proxy = this;
  //this._groupBodyElement.parentNode.removeChild(this._groupBodyElement);
  this.OffsetX = offsetX;
  this.OffsetY = offsetY;
  this.Opacity = opacity;
  this.ShadowColor = shadowColor;
  this.ShadowDirection = shadowDirection;
  this.ApplyFilters();
  //this.RootControl._control.parentNode.appendChild(this._groupBodyElement);
  if (this._groupBodyElement.style.position == "")
    this._groupBodyElement.style.position = "absolute";
}
CustomGroup.prototype.InitSubMenuNew = function(subMenu, offsetX, offsetY, opacity, shadowColor, shadowDirection) {
  this._groupBodyElement = subMenu;
  this._groupBodyElement._proxy = this;
  this.OffsetX = offsetX;
  this.OffsetY = offsetY;
  this.Opacity = opacity;
  this.ShadowColor = shadowColor;
  this.ShadowDirection = shadowDirection;
  this.ApplyFilters();
  this.RootControl._control.parentNode.appendChild(this._groupBodyElement);
  if (this._groupBodyElement.style.position == "")
    this._groupBodyElement.style.position = "absolute";
}
CustomGroup.prototype.ApplyFilters = function() {
  var filter_str = "";
  if (this.Opacity < 100)
  {
    filter_str = "progid:DXImageTransform.Microsoft.Alpha(opacity=" + this.Opacity+ ", style=0);";
    if (this._groupBodyElement.style.filter != null)
      this._groupBodyElement.style.filter = filter_str;
  }
  if (this.ShadowColor != "")
  {
    filter_str = "progid:DXImageTransform.Microsoft.Shadow(color="+this.ShadowColor+", direction="+this.ShadowDirection+", strength=3)";
    if (this._groupBodyElement.style.filter != null)
      this._groupBodyElement.style.filter = filter_str;
  }
}
CustomGroup.prototype.InitTreeGroup = function(id) {
  this._groupBodyElement = c1c_getElementById(id);
}
CustomGroup.prototype.SetPopulated = function () {
  if (this.RootControl.PopulateField)
  {
    if (this.RootControl.PopulateField.value != "")
      this.RootControl.PopulateField.value += ";";
    this.RootControl.PopulateField.value += this.ControlID;
    this.CorrectTheFormPostCollection(this.RootControl.PopulateField.id);
  }
}
CustomGroup.prototype.CorrectTheFormPostCollection = function(id)
{
  var hiddenElement = document.getElementById(id);
  if (hiddenElement)
  {
    if (__theFormPostCollection)
    {
      __theFormPostData = "";
      var count = __theFormPostCollection.length;
      for (var i = 0; i < count; i++) {
        element = __theFormPostCollection[i];
        if (element && element.name == id) {
          element.value = hiddenElement.value;
        }
        __theFormPostData += element.name + "=" + WebForm_EncodeCallback(element.value) + "&";
      }
    }
  }
}
CustomGroup.prototype.InitMenu = function() {
  c1c_attach_event(this._groupBodyElement, this.OnMouseOut, "mouseout");
  c1c_attach_event(this._groupBodyElement, this.OnMouseOver, "mouseover");
  for (var i=0; i<this._count; i++)
  {
    this.Items[i].InitMenu();
  }
}
CustomGroup.prototype.InHierarchy = function(submenu)  {
  if (submenu == this)
    return true;
  for (var i=0; i<this._count; i++)
  {
    if (this.Items[i].InHierarchy(submenu))
      return true;
  }
  return false;
}
CustomGroup.prototype._CollapseAllExceptSingle = function(item, nested)
{
  for (var i=0; i<this.Items.length;  i++)
  {
    var _expanded = this.Items[i].HasSubMenu() && this.Items[i].ChildGroup.Visible(); 
    if (!item && _expanded)
      item = this.Items[i];
    if (this.Items[i] != item && _expanded)
      this.Items[i].ChildGroup.HideTreeGroup(true);
    if (nested && this.Items[i].HasSubMenu())
      this.Items[i].ChildGroup._CollapseAllExceptSingle(null, nested);
  }
}
function C1WebCommandBase ()
{
  this.AllowSelectItem = false;
  this.AllowMultipleSelect = false;
  this.AlwaysHasSelected = false;
  this.AllowUnselectItem = true;
  this.Groups = new Array();
  this.Items  = new Array();
  this.PreloadImages = true;
  this._headersGroup = null;
  this._hasHeaders = false;
  this._groupCount = 0;
  this._itemCount = 0;
  this._isMenu = false;
  this._isTreeView = false;
  this._isToolBar = false;
  this._isTopicBar = false;
  this._isTabStrip = false;
  this._control = null;
  this._horizontalMenu = false;
  this._leftToRight = true;
  this._topToBottom = true;
  this._clickToOpen = false;
  this._menuOpened = false;
  this._inactiveseparator = "";
  this._treeSelectedStatusField = null;
  this._mixedMode = false;
  this._mixedBorderPreActiveImageUrl = "";
  this.SelectedStatusField = null;
  this.PopulateField = null;
  this.Enabled = true;
  this.IsContextMenu = false;
  this._HideSubMenuDelay = 500;
  this._ExpandSinglePath = false;
  this.OnMenuOpened = null;
  this.OnMenuClosed = null;
  this._groupExpandHandler = false;
  this._groupCollapseHandler = false;
}

C1WebCommandBase.prototype.RefreshSelectedItemsStatusField = function() {
  var s = "-1";
  for (var i=0; i<this._itemCount; i++)
  {
    if (this.Items[i].Selected)
    {
      if (s != "")
        s += ";";
      s += i.toString();
    }
  }
  if (this.SelectedItemsStatusField)
  {
    this.SelectedItemsStatusField.value = s;
  }
}
C1WebCommandBase.prototype._IsSingleSelected = function(item)
{
  for (var i=0; i<this._count; i++)
  {
    if (this.Items[i].Selected && this.Items[i] != item)
      return false;
  }
  return true;
}
C1WebCommandBase.prototype.Select = function (item, event) {
  var oldstate = item.Selected;
  var _allowUnselect = this.AllowUnselectItem && (!this.AlwaysHasSelected || this._IsSingleSelected(item));
  if (this.AllowSelectItem)
  {
    item.CancelSelect = false;
    if (item.UserOnSelect && (!item.Selected || _allowUnselect)) 
    {
      item.Selected = true;
      item.UserOnSelect(item, event);
    }
    if (item.CancelSelect)
      return;
    if (_allowUnselect)
      item.Selected = !oldstate;
    else
      item.Selected = true;
    if  (!this.AllowMultipleSelect)
    {
      this.ResetExceptingOne(item);
      this.RefreshSelectedItemsStatusField();
    } 
    else
      this.RefreshSelectedItemsStatusField();
    if (this._mixedMode)
      for (var i=0; i<this._count; i++)
      {
        this.Items[i].Refresh();
      }
    else
      item.Refresh();
  }
  if (!oldstate && item.Selected && item.RaisePostBackOnSelect && item.PostBackFunction)
    item.PostBackFunction()     
}

C1WebCommandBase.prototype.ResetAll = function () {
  this.ResetExceptingOne(null);
}

C1WebCommandBase.prototype.AddGroup = function (group) {
  this.Groups[this._groupCount] = group;
  group.RootControl = this;
  group.Index = this._groupCount;
  this._groupCount++;
  c1c_AllGroups.Add(group);
}
C1WebCommandBase.prototype.AddItem =  function (item) {
  this.Items[this._itemCount] = item;
  item.RootControl = this;
  item.OwnerGroup = this;
  item.Index  = this._itemCount;
  this._itemCount++;
  if (item.RootControl.PreloadImages)
    item.PerformPreloadImages();
}
C1WebCommandBase.prototype.AddHeader = function (controlId, clickJs, selectJs, mousedownJs, mouseenterJs, mouseleaveJs, mousemoveJs, mouseoutJs, mouseoverJs, mouseupJs, mousewheelJs, itemStyle, mouseOverItemStyle, selectedItemStyle, mouseOverSelectedItemStyle, postBackFunc, active, bodyRowId, groupId, groupHeight, handler, itemBackImageUrl, itemImageUrl, itemLeftBorderImageUrl, itemRightBorderImageUrl, mouseOverBackImageUrl, mouseOverImageUrl, mouseOverLeftBorderImageUrl, mouseOverRightBorderImageUrl, selectedBackImageUrl, selectedImageUrl, selectedLeftBorderImageUrl, selectedRightBorderImageUrl, mouseOverSelectedBackImageUrl, mouseOverSelectedImageUrl, mouseOverSelectedLeftBorderImageUrl, mouseOverSelectedRightBorderImageUrl, enabled, canExpandCollapse, callbackProc, callbackWaitControlID, indicatorUrl, selectedIndicatorUrl, mouseOverIndicatorUrl, mouseOverSelectedIndicatorUrl) {
  var item = c1c_init_item(controlId, clickJs, selectJs, mousedownJs, mouseenterJs, mouseleaveJs, mousemoveJs, mouseoutJs, mouseoverJs, mouseupJs, mousewheelJs, itemStyle, mouseOverItemStyle, selectedItemStyle, mouseOverSelectedItemStyle, "",  "", enabled, active, handler, false, true, postBackFunc, itemBackImageUrl, itemImageUrl, itemLeftBorderImageUrl, itemRightBorderImageUrl, mouseOverBackImageUrl, mouseOverImageUrl, mouseOverLeftBorderImageUrl, mouseOverRightBorderImageUrl, selectedBackImageUrl, selectedImageUrl, selectedLeftBorderImageUrl, selectedRightBorderImageUrl, mouseOverSelectedBackImageUrl, mouseOverSelectedImageUrl, mouseOverSelectedLeftBorderImageUrl, mouseOverSelectedRightBorderImageUrl, false, indicatorUrl, selectedIndicatorUrl, mouseOverIndicatorUrl, mouseOverSelectedIndicatorUrl);
  item._isHeader = true;
  item.AllowSelect = canExpandCollapse;
  item._linkedGroupBodyElement = c1c_getElementById(bodyRowId);
  item._linkedGroupElement = c1c_getElementById(groupId);
  if (callbackProc)
    item.InitTreeItemCallback(callbackProc, callbackWaitControlID);
  if (item._linkedGroupElement)
    item._linkedGroupElementHeight = groupHeight;
  if (!this._headersGroup)
  {
    this._headersGroup = c1c_init_group("", true, true, true, true, false, true, true, this._groupCount, "selectedStatusFieldId");
    this._headersGroup.RootControl =  this;
  }
  this._headersGroup.AddItem(item);
}
C1WebCommandBase.prototype.ResetExceptingOne = function (item) {
  if (item._isHeader)
  {
    this._headersGroup.ResetExceptingOne(item);
  } else if (this.Items.length > 0) {
    for (var i=0; i<this.Items.length;  i++)
    {
      if (this.Items[i] != item && item.Selected)
      {
        this.Items[i].Selected = false;
        this.Items[i].Refresh();

        if ((this._isMenu || this._isTreeView) && this.Items[i].ChildGroup && !this.Items[i].ChildGroup.AllowMultipleSelectInControl)
        {
            this.Items[i].ChildGroup.ResetExceptingOne(item);
            this.Items[i].ChildGroup.RefreshSelectedStatusField();
        }
        this.RefreshSelectedStatusFields();
        
      }
      else
      if (this.Items[i] == item && item.Selected && (this._isMenu || this._isTreeView) && this.Items[i].ChildGroup && !this.Items[i].ChildGroup.AllowMultipleSelectInControl)
      {
            this.Items[i].ChildGroup.ResetExceptingOne(item);
            this.Items[i].ChildGroup.RefreshSelectedStatusField();
      }
    }
  }
  else {
    for (var i=0; i<this.Groups.length; i++)
    {
      this.Groups[i].ResetExceptingOne(item);
    }
  }
}
C1WebCommandBase.prototype.RefreshSelectedStatusFields = function() {
  for (var i=0; i<this.Groups.length; i++)
  {
    this.Groups[i].RefreshSelectedStatusField();
  }
}
C1WebCommandBase.prototype.SetGroupStatusField = function(value) {
  var field = c1c_getElementById(value);
  if (field && this._headersGroup)
    this._headersGroup.SelectedStatusField = field;
  if (field && this._isTreeView)
    this._treeSelectedStatusField = field;
}
C1WebCommandBase.prototype.SetGroupOrderField = function(value) {
  var field = c1c_getElementById(value);
  if (field)
    this._groupOrderField = field;
}
C1WebCommandBase.prototype.InitTabStrip = function(inactivesepurl, mixedMode, mixedBorderPreActiveImageUrl, mouseOverMixedBorderPreActiveImageUrl) {
  this._mixedMode = mixedMode;
  this._inactiveseparator = inactivesepurl;
  this._mixedBorderPreActiveImageUrl = mixedBorderPreActiveImageUrl;
  this._mouseOverMixedBorderPreActiveImageUrl = mouseOverMixedBorderPreActiveImageUrl;

  if (this._headersGroup)
  {
    this._headersGroup.AllowMultipleSelect = false;
    this._headersGroup.AllowUnselectItem = false;
  }
}
C1WebCommandBase.prototype.InitTreeControl = function(selectedStatusFieldId, allowSelectItem, allowUnselectItem, allowMultipleSelect, alwaysHasSelected)
{
  this.SelectedItemsStatusField = c1c_getElementById(selectedStatusFieldId);
  this.AllowMultipleSelect = allowMultipleSelect;
  this.AllowUnselectItem = allowUnselectItem;
  this.AllowSelectItem = allowSelectItem;
  this.AlwaysHasSelected = alwaysHasSelected;
}
C1WebCommandBase.prototype.InitTopicBar = function(buttonView, autoCollapse) {
  if (this._headersGroup)
  {
    if (buttonView)
    {
      this._headersGroup.AllowMultipleSelect = false;
      this._headersGroup.AllowUnselectItem = false;
    }
    else
    {
      this._headersGroup.AllowMultipleSelect = !autoCollapse;
      this._headersGroup.AllowUnselectItem = true;
    }
  }
}
C1WebCommandBase.prototype.InitMenu = function(vertical, ltr, ttb, cto, del) {
  this._isMenu = true;
  this._horizontalMenu = !vertical;
  this._leftToRight = ltr;
  this._topToBottom = ttb;
  this._clickToOpen = cto;
  if (del)
    this._HideSubMenuDelay = del;
  for (var i=0; i<this._itemCount; i++)
  {
    this.Items[i].InitMenu();
  }
}
C1WebCommandBase.prototype.InitDefaultContextMenu = function() {
  if(c1c_supportOnContextMenu())
    c1c_attach_event(document, c1_MenuTracker.ShowDefaultContextMenu, "contextmenu");
  else
    c1c_attach_event(document, c1_MenuTracker.ShowDefaultContextMenu, "mouseup");
  c1_MenuTracker.c1_context_menu = this;
  this.IsContextMenu = true;
}
C1WebCommandBase.prototype.InitControlContextMenu = function(id) {
  var control = document.getElementById(id);
  if (!control)
    return;
  c1_MenuTracker.RegisterControlContextMenu(control, this);
  c1c_attach_event(document, c1_MenuTracker.CheckControlAttached, "mousedown");
  control.c1_context_menu = this;
  if(c1c_supportOnContextMenu())
  {
    c1c_attach_event(control, c1_MenuTracker.ShowControlContextMenu, "contextmenu");
  }
  else
  {
    c1c_attach_event(control, c1_MenuTracker.ShowControlContextMenu, "mouseup");
  }
  this.IsContextMenu = true;
}
C1WebCommandBase.prototype.InitCustomContextMenu = function() {
  this.IsContextMenu = true;
}
C1WebCommandBase.prototype.InitTreeView = function(populateFieldName, exps) {
  this._isTreeView = true;
  if (populateFieldName)
    this.PopulateField = document.getElementById(populateFieldName);
  this._ExpandSinglePath = exps;
  if (exps)
    this._CollapseAllExceptSingle(null, true, true);
}
C1WebCommandBase.prototype.setGroupExpandHandler = function()
{
  this._groupExpandHandler = true;
}
C1WebCommandBase.prototype.setGroupCollapseHandler = function()
{
  this._groupCollapseHandler = true;
}
C1WebCommandBase.prototype.OpenMenu = function() {
  this._menuOpened = true;
  if (this.OnMenuOpened)
    this.OnMenuOpened();
}
C1WebCommandBase.prototype.CloseMenu = function() {
  this._menuOpened = false;
  if (this.OnMenuClosed)
    this.OnMenuClosed();
}
C1WebCommandBase.prototype.RootItemClick = function() {
  if (!this._menuOpened)
    this.OpenMenu();
  else if (this._clickToOpen) {
    this.CloseMenu();
  }
}
C1WebCommandBase.prototype._CollapseAllExceptSingle = function(item, nested)
{
  for (var i=0; i<this.Items.length;  i++)
  {
    var _expanded = this.Items[i].HasSubMenu() && this.Items[i].ChildGroup.Visible(); 
    if (!item && _expanded)
      item = this.Items[i];
    if (this.Items[i] != item && _expanded)
      this.Items[i].ChildGroup.HideTreeGroup(true);
    if (nested && this.Items[i].HasSubMenu())
      this.Items[i].ChildGroup._CollapseAllExceptSingle(null, nested);
  }
}
C1WebCommandBase.prototype.set_keyboardSupport = function(value)
{
  this._keyboardSupport = value;
}
C1WebCommandBase.prototype.onHideSubmenu = function(submenu)
{
  if (this._clickToOpen)
    if (!c1_MenuTracker.hasOpenedSubMenus(this) && !c1_MenuTracker.IsActive())
    {

      this._menuOpened = false;
    }
}
C1WebCommandBase.prototype.onDragDrop = function(listEl)
{
  var serData = '';
  if (this.groupSpacing)
  {
    for(var i=0; i<listEl.childNodes.length; i++)
    {
      var node = listEl.childNodes[i];
      if (i == 0)
        node.style.marginTop = '0px';
      else
        node.style.marginTop = this.groupSpacing;
    }
  }
  if (this._groupOrderField)
  {
    for(var i=0; i<listEl.childNodes.length; i++)
    {
      if (serData)
        serData += ';';
      serData += listEl.childNodes[i]._proxy.Index;
    }
    this._groupOrderField.value = serData;
  }
}


function c1c_ReceiveErrorData(data)
{
  alert(data);
}

function c1c_BeforeCallback(par1)
{
}

function c1c_AfterCallback(par1, par2)
{
  c1c_ReceiveServerData(par1);
}

function c1c_ReceiveServerData(data)
{
  var pair = c1c_splitTwice(data, "|");
  if (pair.length == 2)
  {
    var id = pair[0]; 
    var html_and_script = pair[1];
    var go = document.getElementById(id);
    if (go)
    {
      pair = c1c_splitTwice(html_and_script, "|");
      if (pair.length == 2)
      {
        var html_len = parseInt(pair[0]);
        var html = pair[1].substring(0, html_len);
        var script = pair[1].substring(html_len, pair[1].length-1);
        var it = go;
        if (go.tagName != "TR")
        {
          it = c1c_getParentElement(go);

          var ng = document.createElement("div");
          ng.innerHTML = html;
          it.replaceChild(ng.childNodes[0], go);
        }
        else
        {
          it = go.cells[0];
          it.align = "";
          it.innerHTML = html;
        }
        eval(script);
      }
    }
  }
}

function has_disabled_parentNode(pn)
{
  while(pn != null && typeof(pn) != 'undefined')
  {
    if(typeof(pn.disabled) == 'boolean' && pn.disabled)
      return true;
    else if(typeof(pn.enabled) == 'boolean' && !pn.enabled)
      return true;
    else if(typeof(pn.hasAttribute) != 'undefined')
    {
      if(pn.hasAttribute('enabled'))
      {
        var pna = pn.getAttribute('enabled');
        if(typeof(pna) == 'string' && (pna.toLowerCase() == 'disabled' || pna.toLowerCase() == 'false'))
          return true;
        if(typeof(pna) == 'boolean' && !pna)
          return true;
      }
      if(pn.hasAttribute('disabled'))
      {
        var pna = pn.getAttribute('disabled');
        if(typeof(pna) == 'string' && (pna.toLowerCase() == 'disabled' || pna.toLowerCase() == 'true'))
          return true;
        if(typeof(pna) == 'boolean' && pna)
          return true;
      }
    }
    pn = pn.parentNode;
  }
  return false;
}

function c1c_item_disabled_parents(item)
{
  if(typeof(item) != 'undefined')
  {
    if(typeof(item.RootControl) != 'undefined')
    {
      if(typeof(item.RootControl._control) != 'undefined')
      {
        var pn = item.RootControl._control.parentNode;
        return has_disabled_parentNode(pn);
      }
    }
  }
  return false;
}

function c1c_item_onclick(item, event, keyboard)
{
  item.CancelClick = false;
  if (item.Enabled && !c1c_item_disabled_parents(item))
  {
    if ((item.CausesValidation || item.RootControl.causesValidation) && Page_ValidationActive)
    {
      if(typeof(Page_ClientValidate) == "function" && !Page_ClientValidate()) return;
    }
    if (item.UserOnClick && !__c1_designTime) 
      item.UserOnClick(item, event);
    var cl = null;
    if (item.CallbackFunction && !__c1_designTime && !(item.RootControl._isTreeView && c1_TreeViewTracker.GetCheckboxClicked()))
    {
      item.CallbackFunction();
      item.CallbackFunction = null;
      if (item.CallbackWaitControlID != "")
      {
        var c = document.getElementById(item.CallbackWaitControlID);
        if (c)
        {
          if (!c._dontClone)
            c = c.cloneNode(true);
          c.style.display = "";
          c.style.visibility = "";
          if (!c._dontClone)
            cl = c;
        }     
      }
    }
    if (item._linkedGroupBodyElement && cl)
    {
      c1c_append(item._linkedGroupBodyElement, cl);
    }
    if (item.RootControl._isTreeView && item.HasSubMenu() && !c1_TreeViewTracker.GetCheckboxClicked())
    {
      if (item.ChildGroup.Visible())
        item.ChildGroup.HideTreeGroup();
      else
      {
        item.ChildGroup.ShowTreeGroup(cl);
        if (item.RootControl._ExpandSinglePath)
          item.OwnerGroup._CollapseAllExceptSingle(item, false);
      }
    }
    if ((!item.RootControl.enableDragDrop || item._mouseDown) && !item.CancelClick && item.AllowSelect && !c1_TreeViewTracker.GetPlusMinusClicked() && !__c1_designTime)
    {
      item.OwnerGroup.Select(item, event);
      if (!keyboard)
        c1c_item_hover(item);
      else
        c1c_item_endhover(item);
    }
    if (item.CheckClickToOpen() && !item.CancelClick && (!c1_TreeViewTracker.GetPlusMinusClicked() || item.RootControl._groupExpandHandler || item.RootControl._groupCollapseHandler) && !__c1_designTime)
    {
      c1c_clickAnchor(item, c1_TreeViewTracker.GetPlusMinusClicked());
    }
    item.RefreshCheckbox();
    c1_TreeViewTracker.ResetClicked();

    var hcm = false;
    if (item.RootControl._isMenu  && !item.RootControl.IsContextMenu && item.HasSubMenu() && item.IsRootMenuItem())
    {
      if (item.CheckClickToOpen())
      {
        c1_MenuTracker.HideAll();
      }
      item.RootControl.RootItemClick();
    }
    else if (item.RootControl._isMenu  && !item.RootControl.IsContextMenu && !item.IsRootMenuItem())
    {
      hcm = true;
      c1_MenuTracker.HideAll();
    }
    if (item.RootControl.IsContextMenu)
    {
      if (item.CheckClickToOpen() || !item.HasSubMenu())
      {
        c1_MenuTracker.HideContextMenu();
        hcm = true;
      }
      else
      {
        item.RootControl.RootItemClick();
      }
    }

    if (!hcm && !keyboard)
      c1c_item_hover(item);

    if (item.RootControl._isTopicBar)
      c1c_force_ie_layout(item.RootControl._control.style);
  }
}

function c1c_item_onfocus(item, event)
{
  // Clear flag
  item.RootControl._nextKeySubmenu = null;

  // Remember the first link item
  if (!item.RootControl._firstLinkItem)
    item.RootControl._firstLinkItem = item;
  c1c_attach_event(item._boundary, item.OnKeyUp, "keyup");
  c1c_attach_event(item._boundary, item.OnBlur, "blur");
  c1c_item_onmouseover(item, event);
  c1_MenuTracker.ItemIn(item);
}

function c1c_item_onblur(item,  event)
{
  c1c_detach_event(item._boundary, item.OnKeyUp, "keyup");
  c1c_detach_event(item._boundary, item.OnBlur, "blur");
  item.OnMouseOut(event);
  if (item.RootControl._nextKeySubmenu != item.OwnerGroup && item.OwnerGroup._control && item.OwnerGroup.OnMouseOut )
  {
    item.OwnerGroup.OnMouseOut(event);
  }
  if (item.RootControl._firstLinkItem != item)
    item._boundary.removeAttribute('tabIndex');
}

function c1c_item_onkeyup(item, event)
{
  var ev;
  if (window.event) {
    ev = window.event;
  }
  else {
    ev = event;
  }
  var key = (ev ? ev.keyCode : -1);
  if (key == 37)
  {
    c1c_stopEvent(ev);
    item.leftKey(event);
  }
  else if (key == 38)
  {
    c1c_stopEvent(ev);
    item.upKey(event);
  }
  else if (key == 39)
  {
    c1c_stopEvent(ev);
    item.rightKey(event);
  }
  else if (key == 40)
  {
    c1c_stopEvent(ev);
    item.downKey(event);
  }
  else if (key == 13)
  {
    c1c_stopEvent(ev);
    item._mouseDown = true;
    item.OnClick(event);
  }
  else if (item.RootControl._isTreeView && key == 107 && item.ChildGroup && !item.ChildGroup.Visible())
  {
    c1c_stopEvent(ev);
    SetPlusMinusClicked();
    item.OnClick(event);
  }
  else if (item.RootControl._isTreeView && key == 109 && item.ChildGroup && item.ChildGroup.Visible())
  {
    c1c_stopEvent(ev);
    SetPlusMinusClicked();
    item.OnClick(event);
  }
}

function c1c_item_onmousedown(item, event)
{
  item._mouseDown = true;
  if (item.UserOnMouseDown && !__c1_designTime) 
    item.UserOnMouseDown(item, event);
}

function c1c_item_onmouseenter(item, event)
{
  if (item.UserOnMouseEnter && !__c1_designTime) 
    item.UserOnMouseEnter(item, event);
}
function c1c_item_onmouseleave(item, event)
{
  if (item.UserOnMouseLeave && !__c1_designTime) 
    item.UserOnMouseLeave(item, event);
}

function c1c_item_onmousemove(item, event)
{
  item._mouseDown = false;
  if (item.UserOnMouseMove && !__c1_designTime) 
    item.UserOnMouseMove(item, event);
}

function c1c_item_onmouseover(item, event)
{
  if(c1c_item_disabled_parents(item))
    return;
  if (item.Enabled)
  {
    c1c_item_hover(item);
  }
  if (item.UserOnMouseOver && !__c1_designTime) 
    item.UserOnMouseOver(item, event);
  var cursor;
  if (item.Enabled && (item.NavigateUrl != "" || item.RaisePostBackOnClick || item.RaisePostBackOnSelect)) 
    cursor = "pointer";
  else
    cursor = "default";
  item.Item.style.cursor = cursor;
}

function c1c_item_onmouseout(item, event)
{
  if (item.UserOnMouseOut && !__c1_designTime) 
    item.UserOnMouseOut(item, event);
  if (item.Enabled)
    item.Refresh(); 
}

function c1c_item_onmouseup(item, event)
{
  if (item.UserOnMouseUp && !__c1_designTime) 
    item.UserOnMouseUp(item, event);
}

function c1c_item_onmousewheel(item, event)
{
  if (item.UserOnMouseWheel && !__c1_designTime) 
    item.UserOnMouseWheel(item, event);
}


// 
function c1c_item_hover(item)
{
  var style;
  if (item.Selected)
    style = item.MouseOverSelectedItemStyle;
  else
    style = item.MouseOverItemStyle;
  c1c_item_setstyle(item, style, false);
  var imgurl;
  var indurl;
  var backimgurl;
  var leftbordrimgurl;
  var rightbordrimgurl;
  if (!(item.RootControl._mixedMode && item.Index > 0))
  {
    if (!item.Selected)
      leftbordrimgurl = item.MouseOverLeftBorderImageUrl;
    else 
      leftbordrimgurl = item.MouseOverSelectedLeftBorderImageUrl;
  } 
  if (!item.RootControl._mixedMode)
  {
    if (!item.Selected)
      rightbordrimgurl = item.MouseOverRightBorderImageUrl;
    else 
      rightbordrimgurl = item.MouseOverSelectedRightBorderImageUrl;
  } else {
    if (!item.NextIsActive())
    {
      if (!item.Selected)
        rightbordrimgurl = item.MouseOverRightBorderImageUrl;
      else 
        rightbordrimgurl = item.MouseOverSelectedRightBorderImageUrl;
    } else 
      rightbordrimgurl = item.RootControl._mouseOverMixedBorderPreActiveImageUrl;
  }
  if (item.Selected)
  {
    imgurl = item.MouseOverSelectedImageUrl;
    backimgurl = item.MouseOverSelectedBackImageUrl;
    indurl = item.MouseOverSelectedIndicatorUrl;
  }
  else
  {
    imgurl = item.MouseOverImageUrl;
    backimgurl = item.MouseOverBackImageUrl;
    indurl = item.MouseOverIndicatorUrl;
  }
  item.SetBackImageUrl(backimgurl, item._el_mbc);
  item.SetImageUrl(imgurl, item ._el_img);
  item.SetImageUrl(leftbordrimgurl, item._el_lbi);
  item.SetImageUrl(rightbordrimgurl, item._el_rbi);
  item.SetImageUrl(indurl, item._el_ind);
  item.SetFreezWidth(true);
  item.HoverMenuItem();
}

function c1c_item_endhover(item)
{
  var style;
  var imgurl;
  var backimgurl;
  var leftbordrimgurl = "";
  var rightbordrimgurl = "";
  var sepurl;
  var indurl;
  if (!(item.RootControl._mixedMode && item.Index > 0))
  {
    if (!item.Selected)
      leftbordrimgurl = item.LeftBorderImageUrl;
    else 
      leftbordrimgurl = item.SelectedLeftBorderImageUrl;
  } 
  if (!item.RootControl._mixedMode)
  {
    if (!item.Selected)
      rightbordrimgurl = item.RightBorderImageUrl;
    else 
      rightbordrimgurl = item.SelectedRightBorderImageUrl;
  } else {
    if (!item.NextIsActive())
    {
      if (!item.Selected)
        rightbordrimgurl = item.RightBorderImageUrl;
      else 
        rightbordrimgurl = item.SelectedRightBorderImageUrl;
    } else 
      rightbordrimgurl = item.RootControl._mixedBorderPreActiveImageUrl;
  }

  if (item.Selected)
  {
    style = item.SelectedItemStyle;
    imgurl = item.SelectedImageUrl;
    backimgurl = item.SelectedBackImageUrl;
    indurl = item.SelectedIndicatorUrl;
  }
  else
  {
    sepurl = item.RootControl._inactiveseparator;
    if (!item._trackingSubmenu)
    {
      style = item.ItemStyle;
      imgurl = item.ImageUrl;
      backimgurl = item.BackImageUrl;
      indurl = item.IndicatorUrl;
    }
    else
    {
      style = item.MouseOverItemStyle;
      imgurl = item.MouseOverImageUrl;
      backimgurl = item.MouseOverBackImageUrl;
      leftbordrimgurl = item.MouseOverLeftBorderImageUrl;
      rightbordrimgurl = item.MouseOverRightBorderImageUrl;  
    }
  }
  c1c_item_setstyle(item, item._appliedStyle, true);
  c1c_item_setstyle(item, style, false);
  item.SetTabStripSeparatorImageUrl(sepurl);
  item.SetBackImageUrl(backimgurl, item._el_mbc);
  item.SetImageUrl(imgurl, item._el_img);
  item.SetImageUrl(leftbordrimgurl, item._el_lbi);
  item.SetImageUrl(rightbordrimgurl, item._el_rbi);
  item.SetImageUrl(indurl, item._el_ind);
  item.RefreshCheckbox();
  item.EndHoverMenuItem();
  item.SetFreezWidth(item._trackingSubmenu);
}

function c1c_item_setstyle(item, style, reset)
{
  item._appliedStyle = style;
  var itemHtml = item.Item;
  itemHtml.className = "";
  var labelPaddingLeft = "";
  var labelPaddingTop = "";
  var labelPaddingRight = "";
  var labelPaddingBottom = "";

  var ss = style.split(";");
  for (var i = 0; i < ss.length; i++)
  {
    var pair = c1c_splitTwice(ss[i], ":");

    if (pair.length == 2)
      if (pair[0] == "className")
        itemHtml.className = pair[1];
      else if (pair[0]  == "itemImgPos")
      {
        if (c1c_getItemImagePosition(itemHtml) != pair[1])
        {
          c1c_resetItemContent(itemHtml, id);
          c1c_updateItemContent(itemHtml, pair[1]);
        }
      }
      else if (pair[0] == "imgTxSp")
      {
        c1c_updateImgTxSp(itemHtml, pair[1]);
      }
      else if (pair[0] == "LabelPaddingLeft" )
      {
        labelPaddingLeft = pair[1];
      }
      else if (pair[0] == "LabelPaddingRight" )
      {
        labelPaddingRight = pair[1];
      }
      else if (pair[0] == "LabelPaddingTop" )
      {
        labelPaddingTop = pair[1];
      }
      else if (pair[0] == "LabelPaddingBottom" )
      {
        labelPaddingBottom = pair[1];
      }
      else
      {
        if (!reset && typeof(itemHtml.style[pair[0]]) != 'undefined')
          itemHtml.style[pair[0]] = pair[1];
        else if (typeof(itemHtml.style[pair[0]]) != 'undefined')
          itemHtml.style[pair[0]] = "";
      }
  }
  itemHtml.style.display = "none";
  itemHtml.style.display = "";
  c1c_setInnerTextProps(itemHtml);
  item.SetLabelPaddings(labelPaddingLeft, labelPaddingTop, labelPaddingRight, labelPaddingBottom);
}

function c1c_setInnerTextProps(o)
{
  var inTable = o.firstChild;
  if (inTable)
  {
    if (o.currentStyle)
    {
      inTable.rows[1].cells[1].style.color = o.currentStyle.color;
      inTable.rows[1].cells[1].style.fontFamily = o.currentStyle.fontFamily;
      inTable.rows[1].cells[1].style.fontSize = o.currentStyle.fontSize;
      inTable.rows[1].cells[1].style.fontStyle = o.currentStyle.fontStyle;
      inTable.rows[1].cells[1].style.fontVariant = o.currentStyle.fontVariant;
      inTable.rows[1].cells[1].style.fontWeight = o.currentStyle.fontWeight;
      inTable.rows[0].cells[1].style.textAlign = o.currentStyle.textAlign;
      inTable.rows[1].cells[1].style.textAlign = o.currentStyle.textAlign;
      inTable.rows[2].cells[1].style.textAlign = o.currentStyle.textAlign;
      inTable.rows[1].cells[1].style.textDecoration = o.currentStyle.textDecoration;
    }
    else
    {
      inTable.rows[1].cells[1].style.color = o.style.color;
      inTable.rows[1].cells[1].style.fontFamily = o.style.fontFamily;
      inTable.rows[0].cells[1].style.textAlign = o.style.textAlign;
      inTable.rows[1].cells[1].style.textAlign = o.style.textAlign;
      inTable.rows[2].cells[1].style.textAlign = o.style.textAlign;
      inTable.rows[1].cells[1].style.fontSize = o.style.fontSize;
      inTable.rows[1].cells[1].style.fontStyle = o.style.fontStyle;
      inTable.rows[1].cells[1].style.fontVariant = o.style.fontVariant;
      inTable.rows[1].cells[1].style.fontWeight = o.style.fontWeight;
      inTable.rows[1].cells[1].style.textDecoration = o.style.textDecoration;
    }
  }
}

function c1c_clickAnchor(item, plusMinusClicked)
{
  if (item.NavigateUrl != "" && !plusMinusClicked)
  {
    var href = item.NavigateUrl;
    var target = item.Target;
    if (target && href)
    {
      window.open(href, target);
    } else if (href)
    {
      window.document.location.href = href;
    }
  }  
  else if ((item.RaisePostBackOnClick || (item.ChildGroup && (item.RootControl._groupExpandHandler && item.ChildGroup.Visible()) || (item.RootControl._groupCollapseHandler && !item.ChildGroup.Visible()))) && item.PostBackFunction)
    item.PostBackFunction()
}


function c1c_splitTwice(str, ch)
{
  var res = new Array();

  if (str)
  {
    var i = str.indexOf(ch);

    if (i >= 0)
    {
      res[0] = str.substr(0, i);
      res[1] = str.substr(i + 1, str.length);
    }
  }

  return res;
}

// Utils
function c1c_getElementById(id) {
  var result = null;
  if (document.getElementById) {
    result = document.getElementById(id);
  }
  else if (document.all) {
    result = document.all[id];
  }
  else if (document.layers) {
    result = document.layers[id];
  }
  return result;
}

function c1c_attach_event(item, h, eventname)
{
  if (item && item.attachEvent)
    item.attachEvent("on"+eventname, h);
  else if (item && item.addEventListener)
    item.addEventListener(eventname, h, false);
}

function c1c_detach_event(item, h, eventname)
{
  if (item && item.detachEvent)
    item.detachEvent("on"+eventname, h);
  else if (item && item.removeEventListener)
    item.removeEventListener(eventname, h,  false);
}

// Applies color and font of item to first children's table
function c1c_apply_style_to_children(item)
{
  var childColection = null;
  if (item.children)
    childCollection = item.children;
  if (childCollection == null && item.childNodes)
    childCollection = item.childNodes;

  if (childCollection)
  {
    for(var i=0;i<childCollection.length;i++)
    {
      var child = childCollection[i];
      c1c_apply_style_from(child, item);
      c1c_apply_style_to_children(child);
    }
  }
}

function c1c_getsubmenu_x(group, submenu)
{
  var tx;
  var item = group._parentItem.Item;

  if (submenu.style.display == "none")
  {
    submenu.style.visibility = "hidden";
    submenu.style.display = "";
  }

  var parHorz = group._parentItem.IsHorizontal();    
  if (parHorz)
  {
    if (group.RootControl._leftToRight)
      tx = c1c_offset_x(item) - c1c_offset_x(submenu.offsetParent);
    else
      tx = c1c_offset_x(item) - submenu.offsetWidth + item.offsetWidth;
  } else {
    if (group.RootControl._leftToRight)
      tx = c1c_offset_x(item) - c1c_offset_x(submenu.offsetParent) + item.offsetWidth;
    else
      tx = c1c_offset_x(item) - submenu.offsetWidth  - c1c_offset_x(submenu.offsetParent);
  }

  // Smart position
  var docEl;
  if (document.documentElement)
    docEl = document.documentElement;
  else
    docEl = document.body;
  if (tx + submenu.offsetWidth > docEl.clientWidth +  docEl.scrollLeft)
  {
    tx = tx - submenu.offsetWidth - item.offsetWidth + c1c_submenu_offset_right; 
  }
  if (tx <  docEl.scrollLeft && !parHorz)
  {
    if (group.RootControl._leftToRight)
    {
      tx =  docEl.clientWidth +  docEl.scrollLeft - submenu.offsetWidth;
      var par_submenu = group._parentItem.OwnerGroup._groupBodyElement;
      if (par_submenu && (par_submenu.offsetLeft + par_submenu.offsetWidth == tx + submenu.offsetWidth))      
      {
        tx = tx - par_submenu.offsetWidth;
      }
    }
  }
  if (tx <  docEl.scrollLeft)
    tx =  docEl.scrollLeft;
  if (submenu.style.visibility == "hidden")
  {
    submenu.style.display = "none";
    submenu.style.visibility = "";
  }
  return tx;
}

function c1c_getsubmenu_y(group, submenu)
{
  var ty;
  var item = group._parentItem.Item;
  if (submenu.style.display == "none")
  {
    submenu.style.visibility = "hidden";
    submenu.style.display = "";
  }
  var parHorz = group._parentItem.IsHorizontal();    
  if (parHorz)
  {
    if (group.RootControl._topToBottom)
      ty = c1c_offset_y(item) - c1c_offset_y(submenu.offsetParent) + item.offsetHeight;
    else  
      ty = c1c_offset_y(item) - submenu.offsetHeight;
  } else {
    ty = c1c_offset_y(item) - c1c_offset_y(submenu.offsetParent);
    if (!group.RootControl._topToBottom)
      ty = ty - (submenu.offsetHeight - item.offsetHeight);
  }
  // Smart position
  var docEl;
  if (document.documentElement)
    docEl = document.documentElement;
  else
    docEl = document.body;
  if (ty + submenu.offsetHeight > docEl.clientHeight +  docEl.scrollTop)
  {
    ty = ty - submenu.offsetHeight - item.offsetHeight; // + c1c_submenu_offset_right; 
  }
  if (ty <  docEl.scrollTop && !parHorz)
  {
    if (group.RootControl._topToBottom)
    {
      ty =  docEl.clientHeight +  docEl.scrollTop - submenu.offsetHeight;
      var par_submenu = group._parentItem.OwnerGroup._groupBodyElement;
      if (par_submenu && (par_submenu.offsetTop + par_submenu.offsetHeight == ty + submenu.offsetHeight))     
      {
        ty = ty - par_submenu.offsetHeight;
      }
    }
  }
  if (ty <  docEl.scrollTop)
    ty =  docEl.scrollTop;
  if (submenu.style.visibility == "hidden")
  {
    submenu.style.display = "none";
    submenu.style.visibility = "";
  }
  return ty;
}

function c1c_offset_x(o)
{
  if (typeof(o) != 'object' || o == null)
    return 0;
  else
  {
    if (o.style.position != 'relative')
      return o.offsetLeft + c1c_offset_x(o.offsetParent);
    else
      return 0;
  }
}

function c1c_offset_y(o)
{
  if (typeof(o) != 'object' || o == null)
    return 0;
  else
  {
    if (o.style.position != 'relative')
      return o.offsetTop + c1c_offset_y(o.offsetParent);
    else
      return 0;
  }
}

function C1MenuTracker()
{
  this.c1_context_menu = null;
  this.c1_active_context_menu = null;
  this._enteredItem = null;
  this._enteredSubmenu = null;
  this._leftItem = null;
  this._leftSubmenu = null;
  this.Submenus = new Array();
  this.ControlContextMenus = new Array();
  this.RegisterControlContextMenu = function(control, menu)
  {
      this.ControlContextMenus[this.ControlContextMenus.length] = {id:control.id,Menu:menu};
  }
  this.AddSubmenu = function(submenu) {
    var present = false;
    for (var i=0; i<this.Submenus.length; i++)
    {
      if (this.Submenus[i] == submenu)
        present = true;
    }
    if (!present)
      this.Submenus[this.Submenus.length] = submenu;
  }
  this.SubmenuIn = function(submenu) {
    if (this._leftSubmenu == submenu)
      this._leftSubmenu = null;
    this._enteredSubmenu = submenu;
  }
  this.SubmenuOut = function(submenu) {
    if (this._enteredSubmenu == submenu)
      this._enteredSubmenu = null;
    this._leftSubmenu = submenu;
    var _delay = 500;
    if (submenu)
      _delay = submenu.RootControl._HideSubMenuDelay;
    if (window.setTimeout)
      window.setTimeout("c1_MenuTracker.Track();", _delay);
  }
  this.ItemIn = function (item) {
    if (!item.RootControl._isMenu)
      return;
    if (this._leftItem == item)
      this._leftItem = null;
    this._enteredItem = item;
    this.SubmenuIn(item.OwnerGroup);
    this.Track();
  }
  this.ItemOut = function (item) {
    if (!item.RootControl._isMenu)
      return;
    if (this._enteredItem == item)
      this._enteredItem = null;
    this._leftItem = item;
    var _delay = 500;
    if (item)
      _delay = item.RootControl._HideSubMenuDelay;
    if (window.setTimeout)
      window.setTimeout("c1_MenuTracker.Track();", _delay);
  }
  this.Track = function () {
    for (var i=0; i<this.Submenus.length; i++)
    {
      if (!this.Submenus[i].InHierarchy(this._enteredSubmenu) && this.Submenus[i]._parentItem != this._enteredItem && this.Submenus[i].Visible())
        this.Submenus[i].HideSubMenu();
    }
  }
  this.IsActive = function () {
    if (this._enteredItem) 
      return true;
    else
      return false;
  }
  this.OnShowSubmenu = function (submenu) {
    this.AddSubmenu(submenu);
  }
  this.HideAll = function() {
    for (var i=0; i<this.Submenus.length; i++)
    {
      this.Submenus[i].HideSubMenu();
    }
    this.HideContextMenu();
  }
  this.ShowDefaultContextMenu = function (ev) {
    var e = ev;
    if (!ev)      
      e = window.event;
    if(!c1c_supportOnContextMenu() && e.button != 2)
      return true;
    document.body.onmousedown = c1_MenuTracker.HideContextMenuEv;
    if (!c1_MenuTracker.c1_active_menu && !c1_MenuTracker.c1_active_context_menu)
    {
      c1_MenuTracker.ShowContext(c1_MenuTracker.c1_context_menu, e);
    }
    if (e)
    {
      c1c_stopEvent(ev);
    }
    return false;
  }
  this.ShowControlContextMenu = function (ev) {
    var e = ev;
    if (!ev)      
      e = window.event;
    if (e)
      control = c1c_getEventSrc(e);
    control = c1c_getControlContextInParent(control);

    if(!c1c_supportOnContextMenu() && e.button != 2)
      return true;
    document.body.onmousedown = c1_MenuTracker.HideContextMenuEv;
    if (!c1_MenuTracker.c1_active_menu && control && control.c1_context_menu)
    {
      c1_MenuTracker.ShowContext(control.c1_context_menu, e);
    }
    if (e)
    {
      c1c_stopEvent(ev);
    }
    return false;
  }
  this.CheckControlAttached = function (ev) {
    var e = ev;
    if (!ev)      
      e = window.event;
    if(e.button != 2)
      return;
    for (var i=0; i<c1_MenuTracker.ControlContextMenus.length; i++)
    {
      var control = document.getElementById(c1_MenuTracker.ControlContextMenus[i].id);
      if (!control) return;
      if (!control.c1_context_menu)
      {
          control.c1_context_menu = c1_MenuTracker.ControlContextMenus[i].Menu;
          if(c1c_supportOnContextMenu())
          {
            c1c_attach_event(control, c1_MenuTracker.ShowControlContextMenu, "contextmenu");
          }
          else
          {
            c1c_attach_event(control, c1_MenuTracker.ShowControlContextMenu, "mouseup");
          }
       }
    }
  }
  
  this.HideContextMenuEv = function(ev)
  {
    if (!c1_MenuTracker.c1_active_context_menu)
      return;
    var e = ev;
    if (!ev)      
      e = window.event;
    var src = c1c_getEventSrc(e);
    if (src)
    {
      if (!c1_MenuTracker.CheckInMenu(src, c1_MenuTracker.c1_active_context_menu))
        c1_MenuTracker.HideContext(c1_MenuTracker.c1_active_context_menu);
      else
      { 
        if (e.button == 2)
        {
          c1c_stopEvent(ev);
          return false;
        }       
      }
    }
    else
      document.body.onmousemove = c1_MenuTracker.SurelyHideContextMenu;
    document.body.onmousedown = null;
  }
  this.CheckInMenu = function (el, menu) {
    var result = c1c_object_contains(menu._control, el);
    for ( var i=0; i<menu.Items.length; i++)
    {
      if (typeof(menu.Items[i]) == 'object')
      {
        if (menu.Items[i].ChildGroup)
          result = result || this.CheckInMenu(el, menu.Items[i].ChildGroup);
      }
    }
    return result;
  }
  this.HideContextMenu = function ()
  {
    if (c1_MenuTracker.c1_active_context_menu)
    {
      c1_MenuTracker.HideContext(c1_MenuTracker.c1_active_context_menu);
      document.body.onmousemove = null;
    }
  }
  this.SurelyHideContextMenu = function (ev)
  {
    c1_MenuTracker.HideContextMenu();
  }
  this.HideContext = function (menu)
  {
    c1_MenuTracker.c1_active_context_menu = null;
    c1_MenuTracker.HideAll();
    menu._control.style.position = "absolute";
    menu._control.style.visibility = "hidden";
    menu._control.style.left = "0px";
    menu._control.style.top = "0px";
    //c1c_hide_overlay(menu);
    document.body.onmousedown = null;
    document.body.onkeydown = null;
  }
  this.ShowContext = function(menu, ev)
  {
    c1_MenuTracker.c1_active_context_menu = menu;
    menu._control.style.position = "absolute";
    menu._control.style.left = c1c_getContextMenuLeft(menu._control, ev) + "px";
    menu._control.style.top = c1c_getContextMenuTop(menu._control, ev) + "px";
    if (c1c_submenu_zindex)
      menu._control.style.zIndex = c1c_submenu_zindex;
    //c1c_create_and_show_overlay(menu);
    menu._control.style.visibility = "visible";
    menu._control.style.display = "";
  }
  this.ShowContextPos = function (menu, x, y)
  {
    c1_MenuTracker.c1_active_context_menu = menu;
    menu._control.style.position = "absolute";
    menu._control.style.left = x + "px";
    menu._control.style.top = y + "px";
    if (c1c_submenu_zindex)
      menu._control.style.zIndex = c1c_submenu_zindex;
    //c1c_create_and_show_overlay(menu);
    menu._control.style.visibility = "visible";
    menu._control.style.display = "";
  }
  this.hasOpenedSubMenus = function(menu)    
  {
    for (var i=0; i<this.Submenus.length; i++)
    {
      if (this.Submenus[i].RootControl == menu && this.Submenus[i].Visible())
        return true;
    }
    return false;
  }
}

function c1c_object_contains(obj, elem)
{
  try
  {
    if (!obj)
      return null;
    else if (obj.contains)
      return obj.contains(elem);
    else
      return _c1c_object_contains(obj, elem);
  }
  catch (exception)
  {
    return false;
  }
}

function _c1c_object_contains(obj, elem)
{
  if (!obj)
    return null;
  var i;
  if (!obj.childNodes)
    return false;
  for (i = 0; i < obj.childNodes.length; i++) {
    var child = obj.childNodes[i];
    if (elem == child)
      return true;
    else if (_c1c_object_contains(child, elem))
      return true;
  }
  return false;
}

function c1c_supportOnContextMenu()
{
  return true;
}

function c1c_getContextMenuLeft(menu, ev)
{
  var left = 0;
  var cw = document.body.clientWidth;
  var sl = document.body.scrollLeft;
  if (ev.x)
  {
    left = ev.x;
    left = left + sl;
  }
  else if (ev.pageX)
    left = ev.pageX;

  if (left + menu.offsetWidth > sl + cw)
    left = sl + cw - menu.offsetWidth;
  if (left < 0)
    left = 0;
  return left;
}

function c1c_getContextMenuTop(menu, ev)
{
  var top = 0;
  // ANCMD000674
    var docEl;
  if (document.documentElement)
    docEl = document.documentElement;
  else
    docEl = document.body;

  var ch = docEl.clientHeight;
  var st = docEl.scrollTop;
  if (ev.y)
  {
    top = ev.y;
    top = top + st;
  }
  else if (ev.pageY)
    top = ev.pageY;

  if (top + menu.offsetHeight > st + ch)
    top = st + ch - menu.offsetHeight;
  if (top < 0)
    top = 0;
  return top;
}

function c1c_getEventSrc(ev)
{
  var src = null;
  if (ev.srcElement)
    src = ev.srcElement;
  else if (ev.target)
    src = ev.target;  
  return src;
}
function c1c_getControlContextInParent(control)
{
  while (control && !control.c1_context_menu) 
    control = c1c_getParentElement(control);
  return control;
}
function c1c_getParentElement(node)
{
  if (node.parentElement)
    return node.parentElement;
  else if (node.parentNode)
    return node.parentNode;
  else 
    return null;
}

function c1c_hideContextMenu()
{
  c1_MenuTracker.HideContextMenu();
}
function c1c_showContextMenu(id, arg1, arg2)
{
  if (arg2)
    c1c_showContextMenuInternal(id, arg1, arg2);
  else
  {
    var e = arg1;
    if (!e)
      e = window.event;
    var x, y;
    if (e.x)
    { 
      x = e.x;
      if (document.body)
        x += document.body.scrollLeft;
      if (document.documentElement)
        x += document.documentElement.scrollLeft;
    }
    else if (e.pageX)
      x = e.pageX;
    if (e.y)
    { 
      y = e.y;
      if (document.documentElement)
        y += document.documentElement.scrollTop;
      if (document.body)
        y += document.body.scrollTop;
    }
    else if (e.pageY)
      y = e.pageY;
    c1c_showContextMenuInternal(id, x, y);
  }
}
function c1c_showContextMenuInternal(id, x, y) 
{
  var menu = document.getElementById(id);
  document.onmousedown = c1_MenuTracker.HideContextMenuEv;
  c1_MenuTracker.ShowContextPos(menu._proxy, x, y);
}
function C1TreeViewTracker()
{
  this._itemClickedId = false;
  this._itemCheckedId = false;
  this.GetPlusMinusClicked = function(id)
  {
    return this._itemClickedId;
  }
  this.SetPlusMinusClicked = function()
  {
    this._itemClickedId = true;
  }
  this.ResetClicked = function()
  {
    this._itemClickedId = false;
    this._itemCheckedId = false;
  }
  this.GetCheckboxClicked = function(id)
  {
    return this._itemCheckedId;
  }
  this.SetCheckboxClicked = function()
  {
    this._itemCheckedId = true;
  }
}

function SetPlusMinusClicked()
{
  c1_TreeViewTracker.SetPlusMinusClicked();
}
function SetCheckboxClicked()
{
  c1_TreeViewTracker.SetCheckboxClicked();
}

function OnDropDownClick(el, ctxId)
{
  SetPlusMinusClicked();
  var elp = el.offsetParent.offsetParent.offsetParent;
  c1c_showContextMenu(ctxId, c1c_offset_x(elp), c1c_offset_y(elp) + elp.offsetHeight);
}

function C1TreeGroupsGlobal()
{
  this.Groups = new Array();
  this.Add = function(group) {
    this.Groups[this.Groups.length] = group;
  }
  this.Get = function(id) {
    var i;
    for (i = 0; i < this.Groups.length; i++) {
      var child = this.Groups[i];
      if (child.ControlID == id)
        return child;
    }
    return null;
  }
}

function c1c_append(target, source)
{
  if (target.tagName == "TABLE")
    target.rows[0].cells[0].appendChild(source);
  else if (target.tagName == "TR")    
    target.cells[0].appendChild(source);
  else
    target.appendChild(source);
}

var c1c_AllGroups = new C1TreeGroupsGlobal();

function _writeDebug(val)
{
  var de = document.getElementById("_debugger");
  if (de)
  {
    var str = de.innerHTML;
    str += val;
    de.innerHTML = str;
  }
}
function c1c_stopEvent(e) {
  if(!e) var e = window.event;

  //e.cancelBubble is supported by IE - this will kill the bubbling process.
  e.cancelBubble = true;
  e.returnValue = false;

  //e.stopPropagation works only in Firefox.
  if (e.stopPropagation) {
    e.stopPropagation();
    e.preventDefault();
  }
  return false;
}