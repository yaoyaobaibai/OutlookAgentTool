var OFF = false;
var c1g_Props = [];
var c1g_mouseX = 0;
var c1g_mouseY = 0;
var isIE = (navigator.userAgent.toLowerCase().indexOf('msie') != -1);
var isGecko = (navigator.userAgent.toLowerCase().indexOf("gecko") != -1);
var DHTML = (document.getElementById || document.all || document.layers);
var C1G_TOP=0;
var C1G_LEFT=0;

function c1g_state()
{
	this.allowAutoSize = false;
	this.allowColSizing = false;
	this.allowColMoving = false;
	this.allowCbColMoving = false;
	this.allowCbScrolling = false;
	this.cachedEnd = 0;	
	this.cachedStart = 0;	
	this.columns = new Array();
	this.columnLeavesCnt = 0;
	this.correctPos = false;
	this.curGrid = null;
	this.disabled = false;
	this.disposed = false;
	this.dummyDiv = null;
	this.editIdx = -1;
	this.fixedColIndex = -1;
	this.fixedRowsCount = 0;
	this.grid = null;
	this.gridid = null;
	this.grid00 = null;
	this.grid01 = null;
	this.grid10 = null;
	this.grid11 = null;
	this.groupContainer = null;
	this.groupCount = 0;
	this.gcolumns = new Array();
	this.hScroll = 0; //0-none, 1-always, 2-auto
	this.IDGroupedRows = "";
	this.IDResizedCols = "";
	this.isLTR = true;
	this.isLayoutInitiated = false;
	this.imgColDown = null;
	this.imgColUp = null;
	this.loadThruCb = false;
	this.mainDiv = null;
	this.parentDiv = null;
	this.partial = false;
	this.resizedColumns = new Array();
	this.rowsCount = 0;
	this.scrollDiv = null;
	this.scrollInput = null;
	this.scrolling = false;
	this.scrollSize = 0;
	this.scrollStep = 0;
	this.scrollTo = -1;
	this.scrollX = 0;
	this.scrollY = 0;
	this.selectedIdx = -1;
	this.showHeader = false;
	this.spliting = false;
	this.srcIdx = -1;
	this.totalRowsCount = 0;
	this.uniqueid = null;
	this.vScroll = 0;
	
	this.eraseRow = function(idx)
	{
		var ts = this.getLinkedTables(false, idx);
		if (ts[0])
			ts[0].deleteRow(ts[2]);
		
		if (ts[1])
			ts[1].deleteRow(ts[2]);
	}

	this.getLinkedTables = function(byColumn, index)
	{
		var t0 = this.grid;
		var t1 = null;
		var idx = index;

		if (this.spliting)
		{	
			if (byColumn)
			{
				if (index <= this.fixedColIndex)
				{
					t0 = this.grid00;
					t1 = this.grid10;
				}
				else
				{
					t0 = this.grid01;
					t1 = this.grid11;
					idx -= this.fixedColIndex + 1;
				}
			
				if (this.fixedRowsCount == 0)
					t0 = null;
				
				if (this.fixedRowsCount == this.rowsCount)
					t1 = null;
			}
			else
			{
				if (index < this.fixedRowsCount)
				{
					t0 = this.grid00;
					t1 = this.grid01;
				}
				else
				{
					t0 = this.grid10;
					t1 = this.grid11;
					idx -= this.fixedRowsCount;
				}
			
				if (this.fixedColIndex == -1)
					t0 = null;
				else
					if (this.fixedColIndex + 1 == this.columnLeavesCnt)
						t1 = null;
			}
		}

		if (!t0)
		{
			t0 = t1;
			t1 = null;
		}

		return new Array(t0, t1, idx);
	}
	
	this.addRows = function(html, atEnd)
	{
		var tmp = document.createElement("DIV");
		tmp.innerHTML = "<table>" + html + "</table>";
		tmp = tmp.getElementsByTagName("TABLE")[0];
		var rl = tmp.rows.length;
		var fCnt = this.fixedColIndex + 1;
		
		if (this.spliting)
		{
			if (this.allowAutoSize)
				c1g_adjustTableSizes(this, tmp);
		
			var ts = this.getLinkedTables(false, this.fixedRowsCount)
			if (ts[0])
			{
				var tl = ts[0].rows.length;
				for (var i = 0; i < rl; i++) ts[0].insertRow(atEnd ? -1 : 0);
				for (var i = 0; i < rl; i++)
				{
					var newRow = tmp.rows[i];
					if (this.fixedColIndex != -1)
						newRow = c1g_createRowFrom(tmp.rows[i], fCnt, this.columnLeavesCnt - fCnt);
						
					c1g_swapNode(newRow, ts[0].rows[atEnd ? tl + i : i]);
				}
			}
			
			if (ts[1])
			{		
				var tl = ts[1].rows.length;
				for (var i = 0; i < rl; i++) ts[1].insertRow(atEnd ? -1 : 0);
				for (var i = 0; i < rl; i++)
				{
					var newRow = tmp.rows[i];
					if (this.fixedColIndex != -1)
						newRow = c1g_createRowFrom(tmp.rows[i], 0, fCnt);
						
					c1g_swapNode(newRow, ts[1].rows[atEnd ? tl + i : i]);
				}
			}
		}
	}
	
	this.replaceRows = function(idx, html)
	{
		var tmp = document.createElement("DIV");
		tmp.innerHTML = "<table>" + html + "</table>";
		tmp = tmp.getElementsByTagName("TABLE")[0];
		var rl = tmp.rows.length;
		var fCnt = this.fixedColIndex + 1;

		if (this.spliting)
		{
			var ts = this.getLinkedTables(false, idx);
			
			if (ts[0])
			{
				for (var i = 0; i < rl; i++) ts[0].insertRow(ts[2] + i);
				for (var i = 0; i < rl; i++)
				{
					var newRow = tmp.rows[i];
					if (this.fixedColIndex != -1)
						newRow = c1g_createRowFrom(tmp.rows[i], fCnt, this.columnLeavesCnt - fCnt);
						
					c1g_swapNode(newRow, ts[0].rows[ts[2] + i]);
					
					var row = ts[0].rows[ts[2] + i];
					if (row.style.whiteSpace != "")
					{
						var cnt = row.cells.length;
						for (var j = 0; j < cnt; j++)
						{
							var div = row.cells[j].firstChild;
							if (div && div.tagName == "DIV")
								div.style.whiteSpace = "nowrap";
						}
					}
				}
				
				ts[0].deleteRow(ts[2] + rl);				
			}
			
			if (ts[1])
			{		
				for (var i = 0; i < rl; i++) ts[1].insertRow(ts[2] + i);
				for (var i = 0; i < rl; i++)
				{
					var newRow = tmp.rows[i];
					if (this.fixedColIndex != -1)
						newRow = c1g_createRowFrom(tmp.rows[i], 0, fCnt);
					
					c1g_swapNode(newRow, ts[1].rows[ts[2] + i]);

					var row = ts[1].rows[ts[2] + i];					
					if (row.style.whiteSpace != "")
					{
						var cnt = row.cells.length;
						for (var j = 0; j < cnt; j++)
						{
							var div = row.cells[j].firstChild;
							if (div && div.tagName == "DIV")
								div.style.whiteSpace = "nowrap";
						}
					}
				}
				
				ts[1].deleteRow(ts[2] + rl);				
			}
		}
		else
		{
			for (var i = 0; i < rl; i++)
				this.grid.insertRow(idx + i);
			
			for (var i = 0; i < rl; i++)
			{
				var row = this.grid.rows[idx + i];
				row.parentNode.replaceChild(tmp.rows[0], row);
			}
			
			this.eraseRow(idx + rl);		
		}
	}

	
	this.columnCellsIterator = function(colIdx, cbFunc, param)
	{
		var tables = this.getLinkedTables(true, colIdx);
		colIdx = tables[2];
		var shift = 0;
		
		for (var z = 0; z < 2; z++)
			if (tables[z])
		{
			var span = [];
			var rl = tables[z].rows.length;
			var cl = tables[z].rows[0].cells.length;
			
			if (z == 1)
				shift += tables[0].rows.length;
			
			for (var i = 0; i < rl; i++)
			{
				var cells = tables[z].rows[i].cells;
				var ci = 0;
				for (var j = 0; j < cl && j <= colIdx; j++)
				{
					if (span[j])
					{
						span[j]--;
						continue;
					}
					
					var cell = cells[ci];
					if (cell.rowSpan > 1)
						span[j] = cell.rowSpan - 1;
						
					if (j == colIdx)
					{
						var f = cbFunc(this, cell, shift + i, param);
						if (f != true)
							return;
					}
					
					if (cell.colSpan > 1)
						break;
					
					ci++;
				}
			}
		}
	}
	
	this.rowCellsIterator = function(rowIdx, cbFunc, param)
	{
		var t = this.getLinkedTables(false, rowIdx);
		if (t[0])
		{
			var cells = t[0].rows[t[2]].cells;
			var l = cells.length;
			for (var i = 0; i < l; i++)
			{
				var f = cbFunc(this, cells[i], i, param);
				if (f != true) return f;
			}
		}
	
		if (t[1])
		{
			var fi = this.fixedColIndex + 1;
			var cells = t[1].rows[t[2]].cells;
			var l = cells.length;
			for (var i = 0; i < l; i++)
			{
				var f = cbFunc(this, cells[i], i + fi, param);
				if (f != true) return f;
			}
		}
	}
	
	this.scrollToRow = function(idx)
	{
		if (idx >= 0 && (this.hScroll || this.vScroll))
		{
			if (idx >= this.totalRowsCount)
				idx = this.totalRowsCount - 1;
				
			var t = this.getLinkedTables(false, idx);
			if (!t[0]) t[0] = t[1];
			
			if (this.spliting)
			{
				if (idx + 1 > this.fixedRowsCount)
				{
					idx = t[2];
					if (this.allowCbScrolling)
						this.scrollDiv.scrollTop = (idx) * this.scrollStep;
					else
					{
					//..//
					}
				}
			}
			else
			{
			//..//
			}
		}
	}
}

function c1g_baseInit(propsOnly,gridid,uniqueid,fixcolidx,isSplit,scroll,groupcnt,colsize,colmove,cbcolmove,columns,rowsCnt,fixedRowsCnt,hscroll,vscroll,showHdr,selidx,editIdx,cbscroll,cachs,cache,totCount,scrSize,scrTo,autoSize)
{
	if (!c1g_Props[gridid])
		c1g_Props[gridid] = new c1g_state();
	
	var p = c1g_Props[gridid];
	p.allowAutoSize = autoSize;
	p.allowColSizing = colsize;
	p.allowColMoving = colmove;
	p.allowCbColMoving = cbcolmove;
	p.allowCbScrolling = cbscroll;
	p.cachedEnd = cache;
	p.cachedStart = cachs;
	p.columns = columns;
	p.disposed = false;
	p.editIdx = editIdx;
	p.fixedColIndex = fixcolidx;
	p.fixedRowsCount = fixedRowsCnt;
	p.gridid = gridid;
	p.hScroll = hscroll;
	p.groupCount = groupcnt;
	p.gcolumns = new Array();
	p.IDGroupedRows = gridid + "_grows";
	p.IDResizedCols = gridid + "_rcols";
	p.isLTR = c1g_isLTR(gridid);
	p.rowsCount = rowsCnt;
	p.scrolling = scroll;
	p.scrollSize = scrSize;
	p.scrollTo = scrTo;
	p.selectedIdx = selidx;
	p.showHeader = showHdr;
	p.spliting = isSplit;
	p.totalRowsCount = totCount;
	p.uniqueid = uniqueid;
	p.vScroll = vscroll;

	p.columnLeavesCnt = 0;
	for (var i = 0; i < p.columns.length; i++)
		if (p.columns[i].type != 2)
			p.columnLeavesCnt++;

	if (!propsOnly)
	{
		c1g_resetElements(p, gridid);
		c1g_addEvent(document, "mousemove", c1g_trackMouse);
		p.parentDiv.dispose = function() {c1g_dispose(p);}
	}
}


function c1g_dispose(p)
{
	p.disposed = true;
	
	if (typeof(c1g_curAction) != "undefined")
	{
		c1g_clearUIActions();
	}
	
	c1g_removeEvent(document, "mousemove", c1g_trackMouse);
	
	if (!p.disabled)
	{
		if (p.spliting)
		{
			c1g_removeEvent(p.mainDiv, "scroll", c1g_onMainDivScroll);
			c1g_removeEvent(p.scrollDiv, "scroll", c1g_onScroll);
		
			if (isIE)
			{
				c1g_removeEvent(p.mainDiv, "mousewheel", c1g_onMouseWheel);
				c1g_removeEvent(p.scrollDiv, "resize", c1g_scrollDivResize);
			}
		}
		
		if (p.scrolling)
		{
			c1g_removeEvent(p.scrollDiv, "scroll", c1g_onNoSplitScroll);
			if (isIE) c1g_removeEvent(p.scrollDiv, "mousewheel", c1g_onMouseWheel);
		}	
		
		if (typeof(c1g_init) != "undefined")
		{
			c1g_removeEvent(document, "mousedown", c1g_mouseDown);
			c1g_removeEvent(document, "mouseup", c1g_mouseUp);
			c1g_removeEvent(document, "mousemove", c1g_mouseMove);
			c1g_removeEvent(document, "selectstart", c1g_selectStart);
			c1g_removeEvent(window, "resize", new Function("c1g_initHeadPos(c1g_Props['"+p.gridid+"']);"));
			c1g_removeEvent(window, "load", new Function("c1g_ensureHeaders()"));
		}
	}
}

function c1g_resetElements(p, id)
{
	if (p && id)
	{
		p.parentDiv = document.getElementById(id+"_div");
		p.grid = document.getElementById(id);
		p.disabled = c1g_getattr(p.grid, "disabled");
		p.groupContainer = document.getElementById(id+"_groupcontainer");
				
		var cp = (p.grid.cellPadding != "") ? parseInt(p.grid.cellPadding) : 2;
		var cs = (p.grid.cellSpacing != "") ? parseInt(p.grid.cellSpacing) : 0;
				
		if (p.spliting)
			c1g_initSpliting(p);
		else
		{
			if (p.scrolling && (!p.loadThruCb || (p.loadThruCb && !p.partial)))
			{
				var div = document.createElement("DIV");
				var d = div.style;
				var g = (p.groupContainer) ? p.groupContainer.style : p.grid.style;
				div.id = id+"_scrolldiv";
				c1g_processScrollbars(div, p);
				d.position = "relative"; d.left = g.left; d.top = g.top;
				d.width = g.width; d.height = g.height;
				g.position = "relative"; g.left = "0px"; g.top = "0px";

				if (p.groupContainer)
				{
					p.groupContainer.rows[1].cells[0].appendChild(p.grid);
					div.appendChild(p.groupContainer);
				}
				else
					div.appendChild(p.grid);

				p.parentDiv.appendChild(div);
			}
			
			c1g_initNormal(p);
		}
	
		p.dummyDiv = document.getElementById(id+"_dummydiv");
		p.mainDiv = document.getElementById(id+"_maindiv");
		p.scrollDiv = document.getElementById(id+"_scrolldiv");
		p.scrollInput = document.getElementById(id+"_scroll");
		
		if ((p.spliting) && isIE)
			c1g_addEvent(p.scrollDiv, "resize", c1g_scrollDivResize);

		if (p.scrolling)
			c1g_baseScrollingReset(p);

		if (p.spliting)
			c1g_splitingReset(p);
			
		if (p.allowCbScrolling)
			c1g_setVirtualScrollSize(p);

		p.dstIdx = -1;
		p.grpDstIdx = -1;
		p.grpSrcIdx = -1;	
		p.isLayoutInitiated = false;
		p.srcIdx = -1;
	}
}

function c1g_setVirtualScrollSize(p)
{
	p.scrollStep = (isIE) ? Math.floor(p.scrollDiv.clientHeight/ 8) : 19;
	var t = p.getLinkedTables(false, 0);
	p.dummyDiv.style.height = p.scrollDiv.clientHeight + (p.totalRowsCount - t[0].rows.length - 1) * p.scrollStep + "px";
}

function c1g_scrollDivResize(e)
{
	if (!e) e = window.event;

	var id = e.srcElement.id;
	var idx = id.lastIndexOf("_");

	if (idx >= 0)
		id = id.substring(0, idx);

	var p = c1g_Props[id];
	if (p && p.isLayoutInitiated)
	{
		p.isLayoutInitiated = false;
		c1g_reLayout(id);
		if (p.scrollDiv)
		{
			p.scrollDiv.scrollLeft = 0;
			p.scrollDiv.scrollTop = 0;
		}
	}
}


function c1g_initNormal(p)
{
	var cg = c1g_getChildTag(p.grid, "COLGROUP");
	cg = cg.getElementsByTagName("COL");
	
	var clen = p.columns.length;
	for (var i = 0; i < clen; i++)
	{
		var col = p.columns[i];
		if (col.type == 1 || col.type == 3)
			col.cols[col.cols.length] = (col.leftX >= 0) ? cg[col.colTagIdx] : null;
	}
}


function c1g_refreshGrid(id)
{
	var p = c1g_Props[id];
	if (p.isLayoutInitiated)
	{
		c1g_initHeadPos(p);
		
		if (typeof(c1g_reLayout) != "undefined")
			if (p.spliting)
			{
				p.isLayoutInitiated = false;
				c1g_reLayout(id);
			}
	}
}

function c1g_isLTR(gridid)
{
	var grid = document.getElementById(gridid);
	return !(c1g_getattr(grid, "dir") == "rtl");
}


function c1g_getGridID(srcElem)
{
	var res = null;
	
	while (srcElem && !res)
	{
		if (srcElem.tagName == "TABLE" || srcElem.tagName == "DIV")
		{
			var id = c1g_getattr(srcElem, "id");
			
			if (id)
			{
				var i = ((id.indexOf("_groupcontainer") + 1) || (id.indexOf("_maindiv") + 1) || (id.indexOf("_scrolldiv") + 1));
				if (i > 0)
					id = id.substr(0, i - 1);
			
				for (var tmp in c1g_Props)
					if ((typeof(c1g_Props[tmp]) == "object") && (id == tmp))
						res = tmp;
			}
		}

		srcElem = srcElem.parentNode;
	}

	return res;
}

function c1g_getByName(name)
{
	var o = document.getElementById(name);
	if (!o)
	{
		for (var i = 0; i < document.forms.length; i++)
		if (typeof(document.forms[i].elements[name]) != "undefined")
		{
			o = document.forms[i].elements[name];
			break;				
		}
	}
	
	return o;
}


function c1g_getattr(obj, att)
{
	if (obj.getAttribute)
		return obj.getAttribute(att);

	if (obj.attributes)
	{
		var a = obj.attributes[att];
		if (a) return a.value;
	}
	else return obj[att];
}

function c1g_findPos(o)
{
	var X = 0;
	var Y = 0;
	
	if (o.getBoundingClientRect) //IE
	{
		var pos = o.getBoundingClientRect();
		X = pos.left + (document.body.scrollLeft || document.documentElement.scrollLeft);
		Y = pos.top + (document.body.scrollTop || document.documentElement.scrollTop);
	}
	else
		for (; o; o = o.offsetParent)
		{
			X += o.offsetLeft;
			Y += o.offsetTop;
		}

	return [X, Y];
}

function c1g_getChildTag(o, tag)
{
	var tmp = o.getElementsByTagName(tag);
	return (tmp && tmp.length > 0) ? tmp[0] : null;
}

function c1g_addEvent(o, evnt, handler)
{
	if (!o) return;

	if (document.addEventListener)
	{
		if (o != window)
			o.removeEventListener(evnt, handler, true);
		o.addEventListener(evnt, handler, true);
	}
	else
	{
		o.detachEvent("on" + evnt, handler);
		o.attachEvent("on" + evnt, handler);
	}
}

function c1g_removeEvent(o, evnt, handler)
{
	if (document.addEventListener)
		o.removeEventListener(evnt, handler, true);
	else
		o.detachEvent("on" + evnt, handler);
}

function c1g_getChildElements(o)
{
	if (o.children)
		return o.children;
	else
	{
		var res = [];
		for (var i = 0; i < o.childNodes.length; i++)
		{
			if (o.childNodes[i].nodeType == 1)
				res[res.length] = o.childNodes[i];
		}
		return res;
	}
}

function c1g_setColPos(col, elem, idx)
{
	var pos = c1g_findPos(elem);
	col.x = pos[0];
	col.y = pos[1];
	col.xx = col.x + parseInt(elem.offsetWidth);
	col.yy = col.y + parseInt(elem.offsetHeight);
	col.idx = idx;
	col.srcElem = elem;
	return col;
}

function c1g__getThPos(p, c, ci, param)
{
	if (c.tagName == "TH")
	{
		if (param.index < p.columns.length)
		{
			var col = c1g_setColPos(p.columns[param.index], c, param.index);
			if (isIE && p.correctPos && col.leftX > p.fixedColIndex)
			{
				var t = p.getLinkedTables(false, 0);
				var leftSpace = (t[1]) ? t[0].clientWidth : 0;
				t = (t[1]) ? t[1] : t[0];
				var delta = parseInt(t.style.left) - t.offsetLeft + leftSpace;
				col.x += delta;
				col.xx += delta;
			}
		}
		param.index++;
	}
	
	return true;
}

function c1g_initHeadPos(p)
{
	var headIdx = 0;
	var table = p.getLinkedTables(false, 0)[0];

	if (!table.tHead && p.showHeader && p.spliting)
	{
		headIdx = p.fixedRowsCount;
		table = p.getLinkedTables(false, p.fixedRowsCount)[0];
	}

	if (table.tHead)
	{
		var len = table.tHead.rows.length;
		var refvar = new function() {this.index = 0;}
		for (var i = headIdx; i < len + headIdx; i++)
			p.rowCellsIterator(i, c1g__getThPos, refvar);
		refvar = null;
	}
	
	if (p.groupCount >= 0)
	{
		var ga = c1g_getChildElements(document.getElementById(p.gridid+"_Group"))[0];
		if (p.groupCount == 0)
			p.gcolumns[0] = c1g_setColPos(new c1g_c(0,1,1,1,-1,0,-1), ga, -1);
		else
		{
			for (var i = 0; i < p.groupCount; i++)
			{
				var gc = document.getElementById(p.gridid+"_GCOL_"+i);
				if (gc)
				{
					p.gcolumns[i] = c1g_setColPos(new c1g_c(0,1,1,1,i,0,-1), gc, i);
					p.gcolumns[i].x -= 4;
					p.gcolumns[i].xx -= 4;
				}
			}
			
			p.groupCount = p.gcolumns.length;
		}
	}
}

//type : 0 - grouparea column, 1 - column, 2 - band with childs, 3 - band w\o childs.
function c1g_c(allowautosize, allowgroup, allowmove, allowsize, tIndex, type, lx, lxx, cti)
{
	this.allowAutoSize = (allowautosize == 1);
	this.allowGroup = (allowgroup == 1);
	this.allowMove = (allowmove == 1);
	this.allowSize = (allowsize == 1);
	this.cols = [];
	this.srcElem = null;
	this.travIdx = tIndex;
	this.idx = -1;
	this.x = -1;
	this.y = -1;
	this.xx = -1;
	this.yy = -1;
	this.colTagIdx = cti;
	this.leftX = (typeof(lx) == "undefined") ? -1 : lx;
	this.leftXX = (typeof(lxx) == "undefined") ? -1 : lxx;
	this.type = (typeof(type) == "undefined") ? 1 : type;
			
	this.__setCellWidth = function(p, c, idx, param)
	{
		if (c && c.colSpan <= 1)
		{
			var div = c.getElementsByTagName("DIV");
			if (div.length)
				div[0].style.width = param;
		}
		
		return true;
	}
	
	this.setWidth = function(p, value, colsOnly)
	{
		var val = (typeof(value) == "number") ? value + "px" : value;

		var len = this.cols.length;
		for (var i = 0; i < len; i++)
			this.cols[i].width = val;
		
		if (isGecko && !colsOnly)
		{
			if (p.spliting || (val.indexOf("%") > 0))
				p.columnCellsIterator(this.leftX, this.__setCellWidth, val);
				
			if (val.indexOf("%") > 0)
				p.columnCellsIterator(this.leftX, this.__setCellWidth, this.srcElem.offsetWidth + "px");
		}
	}
}

function c1g_copyAttrs(f, t, copyCss, copyID)
{
	if (copyCss)
		t.style.cssText = f.style.cssText;

	for (var i = 0; i < f.attributes.length; i++)
	if (f.attributes[i].specified)
	{
		var val = f.attributes[i].nodeValue;
		if (val && (copyID || (f.attributes[i].name != "id") && (f.attributes[i].name != "name")))
		{
			if (isIE)
				t.attributes[f.attributes[i].nodeName].value = val;
			else
				t.setAttribute(f.attributes[i].nodeName, val);
		}
	}
}

function c1g_processScrollbars(o, p)
{
	if (p.hScroll && p.vScroll && isGecko)
		o.style.overflow="auto";
	else
	{
		switch (p.hScroll)
		{
			case (0):
				if (!isGecko)
					o.style.overflowX="hidden";
				break;
			case (1):
			case (2):
				if (isGecko)
					o.style.overflow="-moz-scrollbars-horizontal";
				else
					if (p.hScroll==1)
						o.style.overflowX="scroll";
					else
						o.style.overflowX="auto";
		}
		
		switch (p.vScroll)
		{
			case (0):
				if (!isGecko)
					o.style.overflowY="hidden";
				break;
			case (1):
			case (2):
				if (isGecko)
					o.style.overflow="-moz-scrollbars-vertical";
				else
					if (p.vScroll==1)
						o.style.overflowY="scroll";
					else
						o.style.overflowY="auto";
		}
	}
}


function c1g_upToTag(item, tag)
{
	while (item && item.tagName && item.tagName.toUpperCase() != tag.toUpperCase())
		item = item.parentNode;
	
	return (item && item.tagName && item.tagName.toUpperCase() == tag.toUpperCase()) ? item : null;
}

function c1g_trackMouse(e)
{
	c1g_mouseX = (typeof(e.pageX) != "undefined") ? e.pageX : event.clientX + (document.body.scrollLeft || document.documentElement.scrollLeft);
	c1g_mouseY = (typeof(e.pageY) != "undefined") ? e.pageY : event.clientY + (document.body.scrollTop || document.documentElement.scrollTop);
}

function c1g_cStyle(el, name)
{
	if (el.currentStyle)
		return el.currentStyle[name];
	else
		return document.defaultView.getComputedStyle(el, null).getPropertyValue(name);
}

function c1g_copyStyle(from, to, untilTag)
{
	//var props1 = new Array("background-color", "border-color", "color", "font-family", "font-style", "font-size", "font-weight", "text-align");
	var props2 = new Array("backgroundColor", "borderColor", "color", "fontFamily", "fontStyle", "fontSize", "fontWeight", "textAlign");

	if (from.currentStyle)
	{
		for (var i in props2)
		{
			var pn = props2[i];
			if (typeof(pn) == "string")
				to.style[pn] = from.currentStyle[pn];
		}
	}
	else
	{
		var hash = [];
		c1g__cStyle(from, hash, untilTag);
			
		/*if (document.defaultView)
		{
			var s = document.defaultView.getComputedStyle(from, "null");
			for (var i in props1)
			{
				if (!hash[props1[i]])
				{
					var val = s.getPropertyValue(props1[i], "");
					if (val && val != "")
						hash[props1[i]] = val;
				}
			}
		}*/
		
		if (!hash["text-align"]) hash["text-align"] = "center";
		
		for (var i in hash)
		{
			var pn = hash[i];
			if (typeof(pn) == "string")
				to.style.setProperty(i, pn, "");
		}
	}
}


function c1g__cStyle(el, hash, untilTag)
{
	var f = true;

	if (el)
	do
	{
		if (el.style)
		{
			var s = el.style.cssText.split(";");
			var len = s.length;
			
			for (var i = 0; i < len; i++)
				if (s[i])
				{
					var pair = s[i].split(":");
					while (pair[0].charAt(0) == " ")
						pair[0] = pair[0].substr(1, pair[0].length - 1);
					
					while (pair[1].charAt(0) == " ")
						pair[1] = pair[1].substr(1, pair[1].length - 1);
					
					pair[0] = pair[0].toLowerCase();
					if (typeof(hash[pair[0]]) == "undefined")
						hash[pair[0]] = pair[1];
				}
		}
	
		f = c1g__cStyle(el.parentNode, hash, untilTag);
	}
	while (f && el.tagName != untilTag)
	
	return false;
}


function c1g_swapNode(from, to)
{
	//if (from.swapNode)
	//	from.swapNode(from, to)
	//else
	//{
		var parent = from.parentNode;
		var sibling = from.nextSibling;
		to.parentNode.replaceChild(from, to);
		parent.insertBefore(to, sibling);
	//}
}


function c1g_createRowFrom(oRow, delFrom, delCnt)
{
	var tab = document.createElement("TABLE");
	var tmp = tab.insertRow(-1);
	tmp.parentNode.appendChild(oRow.cloneNode(true));
	tab.deleteRow(0);

	for (var i = 0; i < delCnt; i++)
		tab.rows[0].deleteCell(delFrom);

	return tab.rows[0];
}

//uses c1g_locking.js stuff
function c1g_adjustTableSizes(p, table)
{
	c1g_setMeasureTable(p);
	
	var rlen = table.rows.length;
				
	var cols = [];
	for (var i = 0; i < p.columns.length; i++)
		cols[i] = parseInt(p.columns[i].cols[0].width);
				
	for (var i = 0; i < rlen; i++)
	{
		var row = table.rows[i];
		if (!c1g_getattr(row, "fix"))
		{
			var clen = row.cells.length;
			for (var j = 0; j < clen; j++)
			{
				if (p.columns[j].allowAutoSize)
				{
					var size = c1g_getSize(row.cells[j], (row.style.whiteSpace == ""), parseInt(p.columns[j].cols[0].width));
					cols[j] = (cols.length <= j) ? size[1] : Math.max(cols[j], size[1]);
				}
			}
		}
	}
				
	for (var i = 0; i < p.columns.length; i++)
		if (parseInt(p.columns[i].cols[0].width) != cols[i])
			p.columns[i].setWidth(p, cols[i], true);

	for (var i = 0; i < rlen; i++)
	{
		var row = table.rows[i];
		var h = 0;
					
		if (!c1g_getattr(row, "fix"))
		{
			var clen = row.cells.length;
			for (var j = 0; j < clen; j++)
			{
				var afWidth = /*(isIE) ? parseInt(row.cells[j].clientWidth) - cp :*/ cols[j];
				var size = c1g_getSize(row.cells[j], true, afWidth);
				var h = Math.max(h, size[0]);
			}
						
			if (h > 0)
			{
				row.style.height = h + "px";
				for (var j = 0; j < clen; j++)
					row.cells[j].firstChild.style.height = h + "px";
			}
		}
	}
				
	c1g_removeMeasureTable();
}