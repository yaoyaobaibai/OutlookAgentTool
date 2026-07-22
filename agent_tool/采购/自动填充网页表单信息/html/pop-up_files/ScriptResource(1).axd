var C1G_ACTION = {NONE:0,MOVEC:1,MOVEGC:2,RESIZE:3};
var c1g_sizeGap = 4;
var c1g_minWidth = 10;
var c1g_moveGap = 2;
var c1g_locked = false;
var c1g_curCol = null;
var c1g_curProp = null;
var c1g_curAction = C1G_ACTION.NONE;
var c1g_dragElement = null;
var c1g_resizeElement = null;
var cX = 0;
var cY = 0;


function c1g_init(id, scrollX, scrollY)
{
	var p = c1g_Props[id];
	
	if (p.scrolling)
	{
		p.scrollDiv.scrollLeft = scrollX;
		p.scrollDiv.scrollTop = scrollY;
	}
	
	if (!p.disabled)
	{
		if (!p.spliting)
			c1g_initHeadPos(p);
	
		c1g_addEvent(document, "mousedown", c1g_mouseDown);
		c1g_addEvent(document, "mouseup", c1g_mouseUp);
		c1g_addEvent(document, "mousemove", c1g_mouseMove);
		c1g_addEvent(document, "selectstart", c1g_selectStart);
		c1g_addEvent(window, "resize", new Function("c1g_initHeadPos(c1g_Props['"+id+"']);"));		
		c1g_addEvent(window, "load", new Function("c1g_ensureHeaders()"));
	}
	
	if (!p.spliting)
		p.isLayoutInitiated = true;
}

function c1g_ensureHeaders()
{
    for (var tmp in c1g_Props)
        if (typeof(c1g_Props[tmp]) == "object")
            c1g_initHeadPos(c1g_Props[tmp]);
}


function c1g_baseScrollingReset(p)
{
	if (!p.disabled)
	{
		c1g_addEvent(p.scrollDiv, "scroll", c1g_onNoSplitScroll);
		if (isIE)
			c1g_addEvent(p.scrollDiv, "mousewheel", c1g_onMouseWheel);
	}
}


function c1g_mouseDown(e)
{
	c1g_trackCursor(e);

	if (c1g_curAction && !c1g_locked && c1g_curCol)
	{
		c1g_locked = true; 
		
		if (c1g_curAction == C1G_ACTION.MOVEC || c1g_curAction == C1G_ACTION.MOVEGC)
			c1g_createDragElement(c1g_curCol.srcElem);
		else
			c1g_createResizeElement(c1g_curProp);
		
		cX = c1g_mouseX; cY = c1g_mouseY;
		
		if (e.preventDefault)
			e.preventDefault();

		return false;
	}
	
	return true;
}

function c1g_mouseMove(e)
{
	if (c1g_curProp && c1g_curProp.disposed)
	{
		c1g_clearUIActions();
		return;
	}

	if (!c1g_locked)
		c1g_trackCursor(e);
	else
	{
		if (isIE && !e.button)
		{
			c1g_mouseUp(e);
			return;
		}
	
		var p = c1g_curProp; 
		if (p.srcIdx != -1 && (c1g_curAction == C1G_ACTION.MOVEC || c1g_curAction == C1G_ACTION.MOVEGC) && c1g_dragElement)
		{
			if (c1g_dragElement.style.display == "none")
			{	
				if ((Math.abs(c1g_mouseX - cX) >= c1g_moveGap) || (Math.abs(c1g_mouseY - cY) >= c1g_moveGap))
					c1g_dragElement.style.display = "";
			} 
	
			if (c1g_dragElement.style.display == "")
			{
				c1g_dragElement.style.left = (parseInt(c1g_dragElement.style.left) + (c1g_mouseX - cX)) + "px";
				c1g_dragElement.style.top = (parseInt(c1g_dragElement.style.top) + (c1g_mouseY - cY)) + "px";
				var draw = false;
				var left = true;
				var item = null;
				var col = c1g_mouseInHeader(e, p) || c1g_mouseInGroupArea(e, p);
				if (col)
				{
					if (col != -1) //move column to the columns or groupcolumns
					{
						item = col.srcElem;
						left = c1g_isLeft(col.srcElem, col.x);
						var sameAreas = ((c1g_curAction == C1G_ACTION.MOVEGC && !col.type) || (c1g_curAction == C1G_ACTION.MOVEC && col.type && col.srcElem.parentNode == p.columns[p.srcIdx].srcElem.parentNode));
						var canGroup = (!col.type) ? ((c1g_curAction == C1G_ACTION.MOVEC && c1g_curCol.allowGroup) || (c1g_curAction == C1G_ACTION.MOVEGC)) : true;
						draw = (!(sameAreas && p.srcIdx == col.idx) && canGroup);

						if (draw && c1g_curAction == C1G_ACTION.MOVEC && col.type)
							draw = !c1g_isParentOf(p.columns[p.srcIdx], col);

						if (draw && sameAreas)
						{
							if (col.idx == p.srcIdx + 1)
								left = !p.isLTR;
							else
								if (col.idx == p.srcIdx - 1)
									left = p.isLTR;
						}
					}
					else //move column to the the grouparea
					{
						if ((c1g_curAction == C1G_ACTION.MOVEC && c1g_curCol.allowGroup) || (c1g_curAction == C1G_ACTION.MOVEGC))
						{
							if (p.groupCount > 0)
							{
								if ((c1g_curAction == C1G_ACTION.MOVEC) || (c1g_curAction == C1G_ACTION.MOVEGC && p.srcIdx != p.groupCount - 1))
								{
									item = p.gcolumns[p.groupCount - 1].srcElem;
									left = !p.isLTR;
									draw = true;
								}
							}
							else
							{
								item = document.getElementById(p.gridid + "_Group");
								left = p.isLTR;
								draw = true;
							}
						}
					}
				}
				else
					if (c1g_mouseInGrid(e, p))
						if (p.columns.length == 0 && !c1g_curCol.type)
						{
							draw = true;
							item = p.grid;
							left = p.isLTR;
						}
						else
						{
							item = c1g_mouseUnderEmptyBand(e, p);
							if (item && item != c1g_curCol)
							{
								left = 2;
								item = item.srcElem;
								draw = true;
							}
						}

				draw ? c1g_showArrows(item, left) : c1g_hideArrows();
			}	
		}
		else 
		if (p.srcIdx != -1 && c1g_resizeElement && c1g_curAction == C1G_ACTION.RESIZE)
		{
			if (c1g_resizeElement.style.display == "none")
			{
				if (Math.abs(c1g_mouseX - cX) > 0)
					c1g_resizeElement.style.display = "";
			}
			c1g_resizeElement.style.left = (parseInt(c1g_resizeElement.style.left) + (c1g_mouseX - cX)) + "px";
		}

		if (((c1g_curAction == C1G_ACTION.MOVEC || c1g_curAction == C1G_ACTION.MOVEGC) && c1g_dragElement.style.display != "none") || (c1g_curAction == C1G_ACTION.RESIZE && c1g_resizeElement.style.display != "none"))
		{
			cX = c1g_mouseX;
			cY = c1g_mouseY;
			
			if (e.preventDefault)
				e.preventDefault();
			
			return false;
		}
	}
	
	if (c1g_curAction)
		return false;
}


function c1g_mouseUp(e)
{
	if (c1g_locked)
	{
		var arg = null;
		var p = c1g_curProp;
		if (c1g_curAction == C1G_ACTION.MOVEC || c1g_curAction == C1G_ACTION.MOVEGC)
		{
			var farg = (c1g_curAction == C1G_ACTION.MOVEC) ? "C" : "G";
			var col = c1g_mouseInHeader(e, p) || c1g_mouseInGroupArea(e, p);
			if (col)
			{
				if (col == -1)
				{
					if ((c1g_curAction == C1G_ACTION.MOVEC && c1g_curCol.allowGroup) || (c1g_curAction == C1G_ACTION.MOVEGC && c1g_curCol.idx != p.groupCount - 1))
						if (c1g_curAction == C1G_ACTION.MOVEC)
							arg = "GroupColMove:" + farg + ":" + p.columns[p.srcIdx].travIdx + ":G:" + p.groupCount;
						else
							arg = "GroupColMove:" + farg + ":" + p.srcIdx + ":G:" + (p.groupCount - 1);
				}
				else
				{
					var idx = col.idx;
					if (idx != -1)
					{
						var targ = (!col.type) ? "G" : "C";
						var sameAreas = ((c1g_curAction == C1G_ACTION.MOVEGC && !col.type) || (c1g_curAction == C1G_ACTION.MOVEC && col.type));

						if (sameAreas)
						{
							var isParent = (c1g_curAction == C1G_ACTION.MOVEGC) ? false : c1g_isParentOf(p.columns[p.srcIdx], col);
							if (idx != p.srcIdx && !isParent)
							{
								var left = c1g_isLeft(col.srcElem, col.x);
								if (Math.abs(p.srcIdx - idx) > 1)
								{
									if (c1g_curAction == C1G_ACTION.MOVEGC)
										if (idx < p.srcIdx)
										{
											if ((p.isLTR && !left) || (!p.isLTR && left)) idx++;
										}
										else
										{
											if ((p.isLTR && left) || (!p.isLTR && !left)) idx--;
										}
								}
								else
								{
									var sameRow = (c1g_curAction == C1G_ACTION.MOVEGC) ? false : col.srcElem.parentNode == p.columns[p.srcIdx].srcElem.parentNode;								
									if (sameRow) left = !(idx > p.srcIdx)
								}

								if (c1g_curAction == C1G_ACTION.MOVEC)
									arg = new Array("ColMove",p.columns[p.srcIdx].travIdx,p.columns[idx].travIdx,left).join(":");
								else
									arg = "GroupColMove:G:" + p.srcIdx + ":G:" + idx;
							}
						}
						else
						if ((c1g_curAction == C1G_ACTION.MOVEGC) || (c1g_curAction == C1G_ACTION.MOVEC && c1g_curCol.allowGroup))
						{
							var left = c1g_isLeft(col.srcElem, col.x);
							if ((c1g_curAction == C1G_ACTION.MOVEC) && ((p.isLTR && !left) || (!p.isLTR && left)))
								idx++;
								
							if (c1g_curAction == C1G_ACTION.MOVEC)
								arg = new Array("GroupColMove",farg,p.columns[p.srcIdx].travIdx,targ,idx).join(":");
							else
								arg = new Array("GroupColMove",farg,p.srcIdx,targ,p.columns[idx].travIdx,left).join(":");
						}
					}
				}
			}
			else
				if (c1g_mouseInGrid(e, p))
					if (!c1g_curCol.type && !p.columns.length)
						arg = "GroupColMove:G:" + p.srcIdx + ":C:0";
					else
					{
						var item = c1g_mouseUnderEmptyBand(e, p);
						if (item && item != c1g_curCol)
							if (farg == "C")
								arg = new Array("ColMove",p.columns[p.srcIdx].travIdx,p.columns[item.idx].travIdx,"true","1").join(":");
							else
								arg = new Array("GroupColMove",farg,p.srcIdx,"C",p.columns[item.idx].travIdx,"false","1").join(":");
					}
			
				//if (p.columns.length == 0 && !c1g_curCol.type && c1g_mouseInGrid(e, p))
				//	arg = "GroupColMove:G:" + p.srcIdx + ":C:0";
			
			c1g_hideArrows();		
			c1g_dragElement.style.display = "none";
		}
		else
			if (c1g_resizeElement)
			{
				c1g_resizeElement.style.display = "none";
	
				var delta = parseInt(c1g_resizeElement.style.left) - c1g_curCol.xx;
				delta += c1g_sizeGap + 1;
						
				var ofsWidth = c1g_curCol.srcElem.offsetWidth; 
				var cp = (p.grid.cellPadding != "") ? parseInt(p.grid.cellPadding) : 1;
				ofsWidth -= cp * 2;
				
				var width = ofsWidth + delta;
				if (width < c1g_minWidth)
					width = c1g_minWidth;
				
				var cWidth = c1g_curCol.cols[0].width;
				if (cWidth.indexOf("%") >= 0)
				{
					var newWidth = Math.floor((parseInt(cWidth)/ ofsWidth) * width);
					if (newWidth < 4) newWidth = 4;
					
					/*var d = newWidth - parseInt(cWidth);
					var d = d / (p.columnLeavesCnt - 1);
					
					for (var i = 0; i < p.columns.length; i++)
						if (i != c1g_curCol.idx && p.columns[i].type != 2)
						{
							cWidth = p.columns[i].cols[0].width;
							if (cWidth.indexOf("%") >= 0)
							{
								var val = Math.floor(parseInt(cWidth) - d);
								if (val <= 0) val = 1;
								p.columns[i].setWidth(p, val + "%");
								
								p.resizedColumns[p.columns[i].travIdx + 1] = val + "%";
							}
						}*/

					width = newWidth + "%";
				}

				var parent = (p.groupContainer) ? p.groupContainer : p.grid;
				parent.style.width = (parent.offsetWidth + delta) + "px";
				
				c1g_curCol.setWidth(p, width);
				if (p.spliting) c1g_refreshGrid(p.gridid);

				p.resizedColumns[c1g_curCol.travIdx + 1] = width;
				p.resizedColumns[0] = parent.style.width;
					
				var f = c1g_getByName(p.IDResizedCols);
				f.value = p.resizedColumns.toString();
					
				c1g_initHeadPos(p);

		}

		c1g_curAction = C1G_ACTION.NONE;
		c1g_locked = false;
		c1g_curCol = null;
		c1g_curProp = null;

		if (arg)
		{
			if (p.allowCbColMoving)
			{
				var cntxt = eval(p.gridid+"_cntxt");
				cntxt.tmp = arg;
				c1cb_doCallback(this,cntxt,arg,null,c1g_afterCbColMoving);
			}
			else
				__doPostBack(p.uniqueid, arg);
		}
	}
}

function c1g_prevent(e)
{
	if (e.preventDefault)
		e.preventDefault();

	return false;
}

function c1g_createDragElement(src)
{
	if (!c1g_dragElement)
	{
		var o = document.createElement("TABLE");
		o.cellPadding = 0;
		o.cellSpacing = 0;
		o.createTHead();
		o.tHead.insertRow(-1);
		o.tHead.rows[0].appendChild(document.createElement("TH"));
		document.body.appendChild(o);
		o.style.zIndex = 1000;
		o.style.position = "absolute";
		o.style.cursor = "pointer";
		c1g_addEvent(o, "click", c1g_prevent);
					
		c1g_dragElement = o;
	}
	
	var th = c1g_dragElement.tHead.rows[0].cells[0];

	th.innerHTML = src.innerHTML;
	c1g_copyStyle(src, th, "TABLE");
	if (parseInt(th.style.borderWidth) > 1)
		th.style.borderWidth = "1px";
	
	th.style.width = ""; th.style.height = ""; th.style.position = "";
	var s = c1g_dragElement.style;
	
	if (th.style.backgroundColor == "transparent" || th.style.backgroundColor == "")
	{
		s.borderLeftStyle=s.borderRightStyle=s.borderTopStyle=s.borderBottomStyle = "solid";
		s.borderLeftWidth=s.borderRightWidth=s.borderTopWidth=s.borderBottomWidth = "1px";
	}
	
	var pos = c1g_findPos(src);
	s.left = pos[0] + "px";
	s.top = pos[1] + "px";
	s.display = "none";
	s.height = parseInt(src.offsetHeight)+"px";
	s.width = parseInt(src.offsetWidth)+"px";
}

function c1g_createResizeElement(p)
{
	var pd = null;
	var sd = null;

	if (!c1g_resizeElement)
	{
		pd = document.createElement("DIV");
		pd.style.width = (c1g_sizeGap * 2 + 2) + "px";
		pd.style.position = "absolute";
		pd.style.zIndex = 1000;
		pd.style.cursor = "w-resize";
		pd.style.backgroundColor = "";
		
		document.body.appendChild(pd);
		c1g_resizeElement = pd;
		
		cd = document.createElement("DIV");
		pd.appendChild(cd);
		cd.style.position = "relative";
		cd.style.left = c1g_sizeGap + "px";
		cd.style.width = "1px";
		cd.style.zIndex = 1000;
		cd.style.cursor = "w-resize";
		cd.style.backgroundColor = "Black";
	}
	
	var s = c1g_resizeElement.style;
	
	s.left = (c1g_curCol.xx - c1g_sizeGap - 2) + "px";
	s.top = (c1g_curCol.y) + "px";
	if (p.spliting || p.scrolling)
	{
		if (p.spliting)
		{
			var tmp = p.columns[0].y - c1g_findPos(p.mainDiv)[1];
			s.height = (parseInt(p.mainDiv.style.height) - tmp) + "px";
		}
		else
		{
			var tmp = p.columns[0].y - c1g_findPos(p.scrollDiv)[1];
			s.height = (parseInt(p.scrollDiv.style.height) - tmp) + "px";
		}
	}
	else
	{
		var cp = parseInt(p.grid.cellSpacing);
		var tf = (p.grid.tFoot) ? p.grid.tFoot.offsetHeight + ((isGecko) ? -cp : 2*cp) : 0;
		s.height = (p.grid.offsetHeight - tf - cp) - c1g_curCol.srcElem.offsetTop + "px";
	}
		
	if (cd)
		cd.style.height = "100%";
}



function c1g__setThCur(p, c)
{
	if (c.tagName == "TH")
		c.style.cursor = "default";
	return true;
}

function c1g__getThByIdx(p, c, ri, param)
{
	if (c.tagName == "TH" && ri == param)
		return c;
	else
		return true;
}

function c1g_trackCursor(e)
{
	if (c1g_curProp)
	{
		var t = c1g_curProp.getLinkedTables(false, 0);
		if (t[0].tHead)
		{
			var len = t[0].tHead.rows.length;
			for (var i = 0; i < len; i++)
				c1g_curProp.rowCellsIterator(i, c1g__setThCur);
		}
	}

	var src = e.srcElement ? e.srcElement : e.target;
	c1g_curAction = C1G_ACTION.NONE;
	
	if (src)
	{
		var id = c1g_getGridID(src);
		if (id && c1g_Props[id])
		{
			var p = c1g_Props[id];
			var col = c1g_mouseInHeader(e, p);
			c1g_curProp = p;
			
			if (col)
			{
				c1g_curProp.srcIdx = col.idx;
				c1g_curCol = col;
				var th = c1g_curCol.srcElem;
				if (p.allowColSizing && col.allowSize && (c1g_mouseX >= col.xx - c1g_sizeGap) && (c1g_mouseX <= col.xx + c1g_sizeGap))
				{
				    if (c1g_curCol.type != 2)
				    {
					  c1g_curAction = C1G_ACTION.RESIZE;
					  th.style.cursor = "w-resize";
					}
				}
				else
					if (p.allowColMoving && col.allowMove)
					{
						c1g_curAction = C1G_ACTION.MOVEC;
						th.style.cursor = "pointer";
					}
			}
			else
			{
				col = c1g_mouseInGroupArea(e, p);
				if (col && col != -1 && col.idx != -1)
				{
					c1g_curProp.srcIdx = col.idx;
					c1g_curCol = col;
					col.srcElem.style.cursor = "pointer";
					c1g_curAction = C1G_ACTION.MOVEGC;
				}
			}
		}
	}
}

function c1g_mouseInHeader(e, p)
{
	var len = p.columns.length;
	var res = null;
	var src = (isIE) ? e.srcElement : e.target;

	if (src != p.scrollDiv)
		for (var i = 0; i < len && !res; i++)
		{
			var col = p.columns[i];
			if ((c1g_mouseX >= col.x && c1g_mouseX <= col.xx) && (c1g_mouseY >= col.y && c1g_mouseY <= col.yy))
				res = col;
		}
	
	return res;
}


function c1g_mouseInGroupArea(e, p)
{
	var ga = document.getElementById(p.gridid+"_Group");
	if (ga)
	{
		var pos = c1g_findPos(ga);
		var pX = c1g_mouseX;
		var pY = c1g_mouseY;
		
		if ((pX > pos[0]) && (pX < pos[0] + parseInt(ga.offsetWidth)) && (pY > pos[1]) && (pY < pos[1] + parseInt(ga.offsetHeight)))
		{
			var len = Math.min(p.groupCount, p.gcolumns.length);
			for (var i = 0; i < len; i++)
			{
				var gc = p.gcolumns[i];
				if ((pX > gc.x) && (pX < gc.xx) && (pY > gc.y) && (pY < gc.yy))
					return gc;
			}
			return -1;
		}
	}
	return null;
}

function c1g_mouseInGrid(e, p)
{
	var pos = c1g_findPos(p.grid);
	if ((c1g_mouseX > pos[0]) && (c1g_mouseX < pos[0] + parseInt(p.grid.offsetWidth)) && (c1g_mouseY > pos[1]) && (c1g_mouseY < pos[1] + parseInt(p.grid.offsetHeight)))
		return true;

	return false;
}

function c1g_mouseUnderEmptyBand(e, p)
{
	var res = null;
	var len = p.columns.length;
	for (var i = 0; i < len && !res; i++)
	{
		var col = p.columns[i];
		if (col.type == 3 && c1g_mouseX >= col.x && c1g_mouseX <= col.xx)
			res = col;
	}
	
	return res;
}

function c1g_clearUIActions()
{
	c1g_curAction = C1G_ACTION.NONE;
	c1g_locked = false;
	c1g_curCol = null;
	
	if (c1g_curProp != null)
	{
		if (c1g_curProp.imgColUp)
			c1g_curProp.imgColUp.style.visibility = "hidden";
	
		if (c1g_curProp.imgColDown)
			c1g_curProp.imgColDown.style.visibility = "hidden";
	}

	if (c1g_dragElement)
		c1g_dragElement.style.display = "none";
	
	if (c1g_resizeElement)
		c1g_resizeElement.style.display = "none";

	c1g_curProp = null;
}

function c1g_hideArrows()
{
	c1g_imgColDown(c1g_curProp).style.visibility = "hidden";
	c1g_imgColUp(c1g_curProp).style.visibility = "hidden";
}

function c1g_isParentOf(drag, dragTo)
{
	if (dragTo.srcElem.parentNode.rowIndex > drag.srcElem.parentNode.rowIndex)
		return (dragTo.leftX >= drag.leftX && dragTo.leftXX <= drag.leftXX);
	
	return false;
}

function c1g_showArrows(o, position)
{
	if (o)
	{
		var imgUp = c1g_imgColUp(c1g_curProp);
		var imgDown = c1g_imgColDown(c1g_curProp);

		var pos = c1g_findPos(o);
		var iW = parseInt(imgUp.offsetWidth)/ 2;

		imgDown.style.top = (pos[1]-imgDown.offsetHeight)+"px";
		imgUp.style.top = (pos[1]+parseInt(o.offsetHeight))+"px";		

		if (typeof(position) == "boolean")
		{
			if (position)
				imgDown.style.left = imgUp.style.left = (pos[0]-iW)+"px";
			else
				imgDown.style.left = imgUp.style.left = (pos[0]+parseInt(o.offsetWidth)-iW)+"px";
		}
		else
			imgDown.style.left = imgUp.style.left = pos[0]+(parseInt(o.offsetWidth)/2)-iW+"px";

		imgUp.style.visibility = "visible";
		imgDown.style.visibility = "visible";
	}
}


function c1g_onMouseWheel(e)
{
	var id = c1g_getGridID(e.srcElement);
	var p = c1g_Props[id];

	if (p && p.scrollDiv)
		p.scrollDiv.scrollTop -= e.wheelDelta

	e.returnValue = false;
}


//IE only
function c1g_selectStart(e)
{
	if (!e) e = window.event;
	
	if (e && c1g_curAction != C1G_ACTION.NONE)
		e.returnValue = false;
}



function c1g_isLeft(o, oXPos)
{
	return (c1g_mouseX < oXPos + (parseInt(o.offsetWidth) / 2));
}


function c1g_imgColDown(p)
{
	if (!p.imgColDown)
	{
		p.imgColDown = document.getElementById(p.gridid + "_ImgColDn");
		if (p.imgColDown && p.imgColDown.parentNode && p.imgColDown.parentNode.tagName != "BODY" && p.imgColDown.parentNode.tagName != "FORM")
		{
			p.imgColDown.parentNode.removeChild(p.imgColDown);
			document.body.appendChild(p.imgColDown);
		}
	}

	return p.imgColDown;
}

function c1g_imgColUp(p)
{
	if (!p.imgColUp)
	{
		p.imgColUp = document.getElementById(p.gridid + "_ImgColUp");
		if (p.imgColUp && p.imgColUp.parentNode && p.imgColUp.parentNode.tagName != "BODY" && p.imgColUp.parentNode.tagName != "FORM")
		{
			p.imgColUp.parentNode.removeChild(p.imgColUp);
			document.body.appendChild(p.imgColUp);
		}
	}

	return p.imgColUp;
}


function c1g_onNoSplitScroll(e)
{
	var src = (isIE) ? e.srcElement : e.currentTarget;
	var id = src.id.substr(0, src.id.lastIndexOf("_"));
	
	var p = c1g_Props[id];
	if (p && p.scrollInput && p.scrollDiv)
		p.scrollInput.value = p.scrollDiv.scrollLeft+","+p.scrollDiv.scrollTop;
		
	if (p.isLayoutInitiated)
		c1g_initHeadPos(p);
}