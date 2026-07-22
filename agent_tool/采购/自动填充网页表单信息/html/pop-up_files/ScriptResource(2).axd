//0-left 1-top 2-right 3-bottom
function c1g_getBorderWidth(table, border)
{
	var bs;
	var bw;
	
	switch(border)
	{
		case 0:
		bs=table.style.borderLeftStyle;
		bw=table.style.borderLeftWidth;
		break;
		
		case 1:
		bs=table.style.borderTopStyle;
		bw=table.style.borderTopWidth;
		break;
		
		case 2:
		bs=table.style.borderRightStyle;
		bw=table.style.borderRightWidth;
		break;
		
		case 3:
		bs=table.style.borderBottomStyle;
		bw=table.style.borderBottomWidth;
		break;
	}
	
	var res = 0;
	
	if (!isGecko)
	{
		if (bs && bs != "none" && bw)
			res = parseInt(bw);

		if (table.border)
			res += parseInt(table.border) * 2;
	}
	
	return res;
}


function c1g_getSubDiv(gn, row, col)
{
	var div = null;
	div=document.getElementById(gn + "_grid" + row + col + "div");
	if (!div)
		div=document.getElementById(gn + "_R1_grid" + row + col + "div");

	return div;
}


function c1g_getSubTable(gn, row, col)
{
	var div=c1g_getSubDiv(gn, row, col);
	if (div)
	{
		var a = div.getElementsByTagName("TABLE");
		if (a && a.length)
			return a[0];
	}

	return null;
}


function c1g_getGridWidth(gn)
{
	var colWidth = 0;
	var div = c1g_Props[gn].mainDiv;
	if (div)
	{
		var a = c1g_getChildTag(div, "TABLE");
		if (a)
			colWidth += c1g_getTableWidth(a, gn);
	}

	return colWidth;
}

function c1g_getGridHeight(gn)
{
	var rowHeight = 0;
	var div = c1g_Props[gn].mainDiv;
	if (div)
	{
		var a = c1g_getChildTag(div, "TABLE");
		if (a)
			rowHeight += c1g_getTableHeight(a);
	}

	return rowHeight;
}

function c1g_getTableWidth(table, gn)
{
	var res = -1;
	
	if (table)
	{
		var cg = table.getElementsByTagName("COLGROUP");
		if (cg.length)
		{
			cg = cg[0].getElementsByTagName("COL");
			var len = cg.length;
			if (len)
			{
				var cs = (table.cellSpacing) ? parseInt(table.cellSpacing) : 0;
				var cp = (table.cellPadding) ? parseInt(table.cellPadding) : 0; 
				if (cs == 0) cs = 2;
				var addSize = (isIE) ? cs*2 + cp*2 : 0;
				
				var mdWidth = c1g_Props[gn].mainDiv.clientWidth;
				res = 0;
				for (var i = 0; i < len; i++)
				{
					var col = cg[i];
					if (col.style.display == "" && col.width != "")
					{
						if (col.width.indexOf("%") == -1)
							res += parseInt(col.width) + addSize;
						else
							if (mdWidth != 0)
								res += (mdWidth / 100) * parseInt(col.width);
					}
				}
			}
		}
		
		return (res != -1) ? res + c1g_getBorderWidth(table, 0) + c1g_getBorderWidth(table, 2) : parseInt(table.offsetWidth);
	}
	
	return 0;
}

function c1g_getTableHeight(table)
{	
	var rowHeight = 0;
	
	if (table)
	{
		//var cs = (table.cellSpacing) ? parseInt(table.cellSpacing) : 0;
		rowHeight = parseInt(table.offsetHeight);// - cs;

		if (rowHeight < 0)
			rowHeight = 0;
	}
	
	return rowHeight;
}

function c1g_getSubGridWidth(gn, row, col)
{
	var table = c1g_getSubTable(gn, row, col);

	if (table)
		return c1g_getTableWidth(table, gn);
		
	return 0;
}


function c1g_getSubGridHeight(gn, row, col)
{
	var table=c1g_getSubTable(gn, row, col);
	if (table)
		return c1g_getTableHeight(table);

	return 0;
}

function c1g_syncDummySize(gn)
{
	var p = c1g_Props[gn];
	var dd = p.dummyDiv;
	if (dd)
	{
		dd.style.width=c1g_getGridWidth(gn) +"px";
		if (p.allowCbScrolling)		
		{
		    c1g_setVirtualScrollSize(p);
		}
		else
			dd.style.height=c1g_getGridHeight(gn) + "px";
	}
}

function c1g_syncMainDivSize(gn)
{
	var p = c1g_Props[gn];
	var sv = p.scrollDiv;
	var gv = p.mainDiv;
	if (sv && gv)
	{
		gv.style.left = parseInt(sv.offsetLeft)+"px";
		gv.style.top = parseInt(sv.offsetTop)+"px";
		gv.style.width = parseInt(sv.clientWidth)+"px";
		gv.style.height = parseInt(sv.clientHeight)+"px";
	}
}

function c1g_resetPos(gn)
{
	var dd = c1g_Props[gn].dummyDiv;
	if (dd)
	{
		dd.style.left = "0px";
		dd.style.top = "0px";
	}
	
	var table00, table01, tale10, table11;

	var div00 = c1g_getSubDiv(gn, 0, 0);
	if (div00)
	{
		div00.style.left = "0px";
		div00.style.top = "0px";
	}

	var div01 = c1g_getSubDiv(gn, 0, 1);
	if (div01)
	{
		div01.style.left = "0px";
		div01.style.top = "0px";
	}

	var div10 = c1g_getSubDiv(gn, 1, 0);
	if (div10)
	{
		div10.style.left = "0px";
		div10.style.top = "0px";
	}
	
	var div11 = c1g_getSubDiv(gn, 1, 1);
	if (div11)
	{
		div11.style.left = "0px";
		div11.style.top = "0px";
	}
}

function c1g_getSubgridsRowHeight(gn, row)
{
	var h1 = c1g_getSubGridHeight(gn, row, 0);
	var h2 = c1g_getSubGridHeight(gn, row, 1); 
	return Math.max(h1, h2);
}

function c1g_getSubgridsColWidth(gn, col)
{
	var w1 = c1g_getSubGridWidth(gn, 0, col); 
	var w2 = c1g_getSubGridWidth(gn, 1, col); 
	return Math.max(w1, w2);
}

function c1g_syncMainTable(gn)
{
	var totalwidth = 0;
	var totalheight = 0;
	var p = c1g_Props[gn];
	var grid = p.grid;
	var md = p.mainDiv;
	if (md)
	{
		var colGroup = c1g_getChildTag(md, "COLGROUP");
		if (colGroup)
		{	
			var colGroups = colGroup.getElementsByTagName("COL");
			if (colGroups && colGroups.length == 2) 
			{
				var v0 = c1g_getSubgridsColWidth(gn, 0);
				if (v0 != 0 && colGroups[0].style.display != "none")
					colGroups[0].width = v0+"px";

				var v1 = c1g_getSubgridsColWidth(gn, 1);
				if (v1 != 0 && colGroups[1].style.display != "none")
					colGroups[1].width = v1+"px";

				if (v0 != 0 && v1 != 0)
					totalwidth = v0 + v1;
				else
					totalwidth = Math.max(v0, v1);
			}
		}
		
		if (grid.rows.length==2)
		{
			var v0 = c1g_getSubgridsRowHeight(gn, 0);
			if (v0 != 0 && grid.rows[0].style.display != "none")
				grid.rows[0].style.height = v0+"px";
				
			grid.rows[1].style.height = "";
			var v1 = c1g_getSubgridsRowHeight(gn, 1);
			if (v1 != 0 && grid.rows[1].style.display != "none")
				grid.rows[1].style.height = v1+"px";
		
			if (v0 != 0 && v1 != 0)
				totalheight = v0 + v1;
			else
				totalheight = Math.max(v0, v1); 
		}

		grid.style.left = "0px";
		grid.style.top = "0px";
		grid.style.width = (totalwidth == 0) ? "" : totalwidth+"px";
		grid.style.height = (totalheight == 0) ? "" : totalheight+"px";

		var a = c1g_getChildTag(md, "TABLE");
		if (a)
		{
			a.style.left = "0px";
			a.style.top = "0px";

			a.style.width = (totalwidth == 0) ? "" : totalwidth+"px";
			a.style.height = (totalheight == 0) ? "" : totalheight+"px";
		}	
		
		var tmp = document.getElementById(gn+"_btmpgr");
		if (tmp) tmp.style.top = "0px";
			
		tmp = document.getElementById(gn + "_toppgr");
		if (tmp) tmp.style.top = "0px";
		
		if (p.groupContainer)
		{
			p.groupContainer.style.width = totalwidth + "px";
			grid.style.width = "100%";
		}
	}
	
	/*for (var i = 0; i < p.columns.length; i++)
	{
		var col = p.columns[i];
		if (col.cols.length > 1)
		{
			var diff = col.cols[0].offsetWidth - col.cols[1].offsetWidth;
			if (diff)
			{
				diff = parseInt(col.cols[1].width) + diff;
				if (diff > 0)
					col.cols[1].width = diff;
			}
		}
	}*/
}

function c1g_onMainDivScroll(e)
{
	var src = (isIE) ? e.srcElement : e.currentTarget;
	var idx = src.id.lastIndexOf("_");
	tmp = src.id.substr(0, idx);

	var p = c1g_Props[tmp];
	if (p)
	{
		var mv = p.mainDiv;
		var sv = p.scrollDiv;

		var i = parseInt(sv.scrollLeft);
		i += parseInt(mv.scrollLeft);
		sv.scrollLeft = i;

		i = parseInt(sv.scrollTop);
		i += parseInt(mv.scrollTop);
		sv.scrollTop = i;

		mv.scrollLeft=0;
		mv.scrollTop=0;
	}
}

function c1g_onScroll(e)
{
	var tmp = null;
	if (typeof(e) == "string")
		tmp = e;
	else
	{
		var src = (isIE) ? e.srcElement : e.currentTarget;
		var idx = src.id.lastIndexOf("_");
		tmp = src.id.substr(0, idx);
	}

	var p = c1g_Props[tmp];
	var sv=p.scrollDiv;
	
	if (sv)
	{
		var svl = parseInt(sv.scrollLeft);
	
		if (svl!=C1G_LEFT)
		{
			var table01 = p.grid01;
			if (table01)
				table01.style.left=(-svl)+"px";

			var table11 = p.grid11;
			if (table11)
				table11.style.left=(-svl)+"px";

			C1G_LEFT=svl;
			
			if (isIE) p.correctPos = true;
		}

		var svt = parseInt(sv.scrollTop);
		if (svt!=C1G_TOP)
		{
			var table10 = p.grid10;
			var table11 = p.grid11;
			
			if (table10)
				table10.style.top=(-svt)+"px";
		
			if (table11)
				table11.style.top=(-svt)+"px";
		
			pager = document.getElementById(tmp + "_btmpgr");
			if (pager)
				pager.style.top=(-svt)+"px"; 

			C1G_TOP=svt;
		}

		if (p.scrollInput && !p.allowCbScrolling)
			p.scrollInput.value = C1G_LEFT+","+C1G_TOP;
	}

	if (p.isLayoutInitiated)
	{
		c1g_initHeadPos(p);
		if (isIE) p.correctPos = false;
	}
}


function c1g_onfocus(evnt, id, tid)
{
	var el = (evnt.srcElement) ? evnt.srcElement : evnt.target;

	if (el && el.parentNode && el.parentNode.parentNode && el.parentNode.parentNode.tagName == "TD")
	{
		var sd = c1g_Props[id].scrollDiv;
		var ol = el.parentNode.parentNode.offsetLeft;
		var ot = el.parentNode.parentNode.offsetTop;
		el = el.offsetParent;
		
		while (el)
		{
			if (el.id == id+"_"+tid)
			{
				if (sd && parseInt(el.style.left) < 0)
				{
					var sl = -parseInt(el.style.left);
					if (ol < sl) sd.scrollLeft = parseInt(sd.scrollLeft) + ol - sl - 1;
				}
				
				if (sd && parseInt(el.style.top) < 0)
				{
					var st = -parseInt(el.style.top);
					if (ot < st) sd.scrollTop = parseInt(sd.scrollTop) + ot - st - 1;
				}
				
				if (isGecko)
					c1g_onScroll(id);
				
				break;
			}
			el = el.offsetParent;
		}
	}
}


function c1g_layout(gn, scrollX, scrollY)
{
	var p = c1g_Props[gn];
	p.scrollX = scrollX;
	p.scrollY = scrollY;

	//if (!p.loadThruCb)
	//	c1g_addEvent(window, "load", c1g_wndLoad);
	//else
		c1g_baseLayout(gn);
}

function c1g_wndLoad(sender)
{
	for (var id in c1g_Props)
		if (typeof(c1g_Props[id]) == "object" && !c1g_Props[id].isLayoutInitiated)
			c1g_baseLayout(id);
}


function c1g_baseLayout(gn)
{
	var p = c1g_Props[gn];
	var sd = p.scrollDiv;	

	c1g_syncMainTable(gn);

	if (p.allowAutoSize)
	{
		c1g_adjustSize(p);
		c1g_syncMainTable(gn); //recalculate sizes again
	}

	c1g_syncDummySize(gn);
	c1g_resetPos(gn);
	c1g_syncMainDivSize(gn);

	if (!p.allowCbScrolling)
	{
		C1G_TOP = C1G_LEFT = 0;
		sd.scrollTop = p.scrollY;
		sd.scrollLeft = p.scrollX;
	}
	else
	{
		if (p.scrollTo != -1)
			sd.scrollTop = C1G_TOP = p.scrollY = p.scrollStep * p.scrollTo;
		else
			sd.scrollTop = C1G_TOP = p.scrollY;
	
		sd.scrollLeft = C1G_LEFT = p.scrollX;
	}
	
	p.isLayoutInitiated = true;		
		
	c1g_initHeadPos(p);
}


function c1g_reLayout(gn)
{	
	var p = c1g_Props[gn];

	if (!p.isLayoutInitiated)
	{
		c1g_syncMainTable(gn);
		
		c1g_syncDummySize(gn);
		c1g_syncMainDivSize(gn);
		c1g_onScroll(gn);
		
		p.isLayoutInitiated = true;
	}		
}


function c1g_splitLayout(e)
{
	var src = e.srcElement ? e.srcElement : e.target;
	
	if (src)
	{
		var id = c1g_getGridID(src);
		if (c1g_Props[id] && c1g_Props[id].isLayoutInitiated && c1g_curAction == C1G_ACTION.NONE)
			c1g_reLayout(id);
	}
}


function c1g_splitingReset(p)
{
	var id = p.gridid;
	p.grid00 = c1g_getSubTable(id, 0, 0);
	p.grid01 = c1g_getSubTable(id, 0, 1);
	p.grid10 = c1g_getSubTable(id, 1, 0);
	p.grid11 = c1g_getSubTable(id, 1, 1);
	
	if (!p.disabled)
	{
		/*if (p.grid00)
			c1g_addEvent(p.grid00, "resize", c1g_splitLayout);

		if (p.grid01)
			c1g_addEvent(p.grid01, "resize", c1g_splitLayout);*/
		
		if (p.mainDiv)
		{
			c1g_addEvent(p.mainDiv, "scroll", c1g_onMainDivScroll);
	
			if (isIE)
				c1g_addEvent(p.mainDiv, "mousewheel", c1g_onMouseWheel);
		}
		
		if (p.scrollDiv)
		{
			if (p.allowCbScrolling)
				c1g_addEvent(p.scrollDiv, "scroll", c1g_cbOnScroll);
			else
				c1g_addEvent(p.scrollDiv, "scroll", c1g_onScroll);
		}
			
		if (!p.disabled)
		{
			var evnt = (isIE) ? "focusin" : "focus";
			c1g_addEvent(p.grid00, evnt, new Function("event", "c1g_onfocus(event,\""+id+"\",\"grid00\")"));
			c1g_addEvent(p.grid01, evnt, new Function("event", "c1g_onfocus(event,\""+id+"\",\"grid01\")"));
			c1g_addEvent(p.grid10, evnt, new Function("event", "c1g_onfocus(event,\""+id+"\",\"grid10\")"));
			c1g_addEvent(p.grid11, evnt, new Function("event", "c1g_onfocus(event,\""+id+"\",\"grid11\")"));
		}
	}
}

function c1g_correct(t)
{
	if (t.tBodies.length == 1 && t.tBodies[0].rows.length == 1 && t.tBodies[0].rows[0].style.display == "none" &&
		t.tBodies[0].rows[0].cells.length == 1 && t.tBodies[0].rows[0].cells[0].innerHTML == "&nbsp;")
		t.tBodies[0].deleteRow(0);
	
	return t;
}

function c1g_initSpliting(p)
{
	var alwaysCreated = (document.getElementById(p.gridid + "_scrolldiv") != null);
	var t00 = c1g_correct(document.getElementById(p.gridid + "_grid00"));
	var t01 = c1g_correct(document.getElementById(p.gridid + "_grid01"));
	var t10 = c1g_correct(document.getElementById(p.gridid + "_grid10"));
	var t11 = c1g_correct(document.getElementById(p.gridid + "_grid11"));
	var fixedCount = p.fixedColIndex + 1;
	
	c1g_addCOLS(p, t00, t10, t01, t11);

	var clen = p.columnLeavesCnt;
	var rlen = p.rowsCount;
	var uRows = p.rowsCount - p.fixedRowsCount;
	var uCols = clen - fixedCount;
	
	if (clen == 0 && p.groupCount > 0) uCols = 1;
		
	if (!alwaysCreated)
	{
		var s = (!p.groupContainer) ? p.grid.style : p.groupContainer.style;
		var sd = document.createElement("DIV");	sd.id = p.gridid+"_scrolldiv";
		var t = sd.style; t.position="relative"; /*t.left=s.left; t.top=s.top;*/ t.overflow="hidden";
		//t.height="0px"; t.width="0px";
		t.left=t.top="0px";
		t.height=t.width="100%";
		c1g_processScrollbars(sd, p);
			
		var dd = document.createElement("DIV");	dd.id = p.gridid+"_dummydiv";
		sd.appendChild(dd); t = dd.style; t.overflow="hidden"; t.position="relative"; t.left="0px";	t.top="0px"; t.width="100%"; t.height="100%";
	
		var md = document.createElement("DIV");	md.id = p.gridid+"_maindiv";
		t = md.style; t.overflow="hidden"; t.position="absolute"; t.width=s.width; t.height=s.height;
		/*t.left=s.left; t.top=s.top;*/
		t.left=t.top="0px";
	
		var pgr = document.getElementById(p.gridid+"_toppgr");
		if (pgr)
		{
			c1g_copyAttrs(p.grid, pgr, true, false);
			c1g_resetPgrStyle(pgr);
			pgr.style.zIndex = (p.grid.style.zIndex != "") ? p.grid.style.zIndex + 5 : 5;
		}
	
		pgr = document.getElementById(p.gridid+"_btmpgr");
		if (pgr)
		{
			c1g_copyAttrs(p.grid, pgr, true, false);
			c1g_resetPgrStyle(pgr);
		}

		p.parentDiv.appendChild(sd);
		p.parentDiv.appendChild(md);
	
		t = document.getElementById(p.gridid+"_maintable");		
		if (!p.groupContainer)
		{
			p.parentDiv.removeChild(p.grid);
			md.appendChild(t);
		}
		else
		{
			s = p.grid.parentNode;
			s.replaceChild(t, p.grid);
			md.appendChild(p.groupContainer);
		}

		if (fixedCount > 0)
		{
			if (p.fixedRowsCount > 0) //00
				c1g_unspan(p, p.grid, t00, 0, 0, p.fixedRowsCount, fixedCount);

			if (uRows > 0) //10
				c1g_unspan(p, p.grid, t10, p.fixedRowsCount, 0, uRows, fixedCount);
		}

		if (uCols > 0)
		{
			if (p.fixedRowsCount > 0) //01
				c1g_unspan(p, p.grid, t01, 0, fixedCount, p.fixedRowsCount, uCols);
			
			if (uRows > 0) //11
				c1g_unspan(p, p.grid, t11, p.fixedRowsCount, fixedCount, uRows, uCols);
		}
		
		c1g_removeCells(t00);
		c1g_removeCells(t01);
		c1g_removeCells(t10);
		c1g_removeCells(t11);

		t.id = p.gridid;
		p.grid = t;
	}
}

function c1g_removeCells(t)
{
	if (t.tHead)
	{
		var len = t.tHead.rows.length;
		for (var i = 0; i < len; i++)
		{
			var row = t.tHead.rows[i];
			var clen = row.cells.length;
			for (var j = 0; j < clen; j++)
				if (row.cells[j].abbr == "c1wg_temp")
				{
					row.deleteCell(row.cells[j].cellIndex);
					j--;
					clen--;
				}
		}
	}
}


function c1g_buildCOLarray(t0, t1, arr)
{
    var cg0 = t0.getElementsByTagName("COLGROUP");
    cg0 = (cg0.length) ? cg0[0].getElementsByTagName("COL") : null;
    
    var cg1 = t1.getElementsByTagName("COLGROUP");
    cg1 = (cg1.length) ? cg1[0].getElementsByTagName("COL") : null;
    
    var len = (cg0) ? cg0.length : 0;
    if (!len && cg1)
        len = cg1.length;
        
    for (var i = 0; i < len; i++)
    {
        if (cg0 && cg1)
            arr[arr.length] = [cg0[i], cg1[i]];
        else
        {
            if (cg0)
                arr[arr.length] = [cg0[i]];
            
            if (cg1)
                arr[arr.length] = [cg1[i]];
        }
    }
}


function c1g_addCOLS(p, t0, t1, t2, t3)
{
   var colsarr = [];
   
   c1g_buildCOLarray(t0, t1, colsarr);
   c1g_buildCOLarray(t2, t3, colsarr);
   
   var len = p.columns.length;
   for (var i = 0; i < len; i++)
   {
     var col = p.columns[i];
     
     if (col.type != 2)
     {
        var entry = colsarr[col.colTagIdx];
        if (entry)
        {
            for (var j = 0; j < entry.length; j++)
               col.cols[col.cols.length] = entry[j];
        }
     }
   }
}

function c1g_resetPgrStyle(pgr)
{
	pgr.style.borderBottomStyle="solid"; pgr.style.borderBottomWidth="1px";
	pgr.style.position="relative";pgr.style.height=""; pgr.style.left=pgr.style.top = "";
	pgr.style.display="";		
	pgr.cellSpacing=0;
}

function c1g_span(span, hspan)
{
	this.span = span;
	this.vSpan = 1;
	this.hSpan = hspan;
}

function c1g_unspan(p, oTable, sTable, oRowStart, oColStart, rlen, clen)
{
	var span = [];
	var ci = 0;
	var cj = 0;
	if (!isIE) sTable.style.display="none";
	rlen = Math.min(rlen, sTable.rows.length);
	
	for (var i = 0; i < rlen; i++)
	{
		var hSpan = 0;
		var totSpan = 0;
		var hasNoSpan = true;
		
		var oRow = oTable.rows[oRowStart + i];
		
		if (oRow.style.display == "none" && oRow.cells.length == 1 && oRow.cells[0].innerHTML == "&nbsp;")
		{
			if (oRowStart + i < oTable.rows.length)
			{
				oRowStart++;
				i--;
			}
			continue;
		}
		
		for (var j = 0; j < clen; j++)
		{
			ci = i;
			cj = j;
	
			if (span[j])
			{
				cj = cj - span[j].hSpan;
				ci = ci - span[j].vSpan;				
				if (hasNoSpan) hSpan = 0;
				hSpan++;
				totSpan++;
				span[j].vSpan++;
				hasNoSpan = false;
			}
			else
			{
				hasNoSpan = true;
				cj = cj - totSpan;
			}

			var sRow = sTable.rows[ci];
			var cell = sRow.cells[cj];
		
			if (cell)
			{			
				if (hasNoSpan && cell.rowSpan > 1 && cell.tagName != "TH")
					span[j] = new c1g_span(cell.rowSpan, hSpan);
				
				if (cell.colSpan > 1 && cell.tagName != "TH")
				{
					var len = sRow.cells.length;
					for (var t = 0; t < len; t++)
						sRow.cells[t].innerHTML = oRow.cells[t].innerHTML;
					break;
				}
			
				if (hasNoSpan)
				{
					var nowrap = (sRow.style.whiteSpace != "" || cell.style.whiteSpace != "");

					var oCell = oRow.cells[oColStart + j];
					while (oCell.firstChild)
					    cell.appendChild(oCell.firstChild);
                    //cell.innerHTML = oRow.cells[oColStart + j].innerHTML;					    
				
					var div = null;
					if (nowrap && (div = cell.firstChild) && div.tagName == "DIV")
						div.style.whiteSpace = "nowrap";
				}
			}	
		}

		for (var t in span)
			if (span[t] && (typeof(span[t]) == "object") && (span[t].span == span[t].vSpan))
				span[t] = null;
	}

	if (!isIE) sTable.style.display="";
}

var c1g_columns = null;
var c1g_mTable = null;
var c1g_rows = null;

function c1g_adjustSize(p)
{
	c1g_columns = [];
	
	for (var i = 0; i < p.columns.length; i++)
	{
	    var col = p.columns[i];
   		c1g_columns[i] = (col.cols.length) ? parseInt(col.cols[0].width) : null;
	}

	c1g_setMeasureTable(p);

	for (var i = 0; i < p.rowsCount; i++)
		p.rowCellsIterator(i, c1g__adjustWidth, null);
		
	for (var i = 0; i < p.columns.length; i++)
	{
	    var col = p.columns[i];
		if ((c1g_columns[i] != null) && (parseInt(col.cols[0].width) != c1g_columns[i]))
			col.setWidth(p, c1g_columns[i], true);
	}

	var param = new function()
	{
		this.lastIndex = this.max = -1;
		this.ri = 0;
		this.cp = p.grid00.cellPadding ? parseInt(p.grid00.cellPadding) * 2 : 2;
	}

	c1g_rows = [];
	for (var i = 0; i < p.rowsCount; i++)
	{
		param.lastIndex = p.columns.length - 1;
		param.max = -1;
		p.rowCellsIterator(i, c1g__adjustHeight, param);
	}
	
	param = null;
	
	c1g_removeMeasureTable();
	
	for (var i = 0; i < c1g_rows.length; i++)
	{
		var t = p.getLinkedTables(false, i);
		var h;
		for (var j = 0; ((h = c1g_rows[i]) > 0) && (j < 2) && t[j]; j++)
		{
			var row = t[j].rows[t[2]];
			row.style.height = h + "px";
				
			var clen = row.cells.length;
			for (var ci = 0; ci < clen; ci++)
			{
				var fs = row.cells[ci].firstChild;
				if (fs && fs.tagName == "DIV")
					fs.style.height = h + "px";
			}
		}
	}
}

function c1g_setMeasureTable(p)
{
	if (!c1g_mTable)
	{
		c1g_mTable = document.createElement("table");
		c1g_mTable.cellPadding = p.grid00.cellPadding;
		c1g_mTable.style.visibility = "hidden";		
		c1g_mTable.insertRow(-1);
		c1g_mTable.rows[0].insertCell(-1);
		document.body.appendChild(c1g_mTable);		
	}
}

function c1g_removeMeasureTable()
{
	document.body.removeChild(c1g_mTable);
	c1g_mTable = null;
}

function c1g__adjustHeight(p, c, ci, param)
{	
	var row = c.parentNode;
	
	if (p.columns[ci].allowAutoSize && !c1g_getattr(row, "fix"))
	{
		var afWidth = (isIE) ? parseInt(c.clientWidth) - param.cp : c1g_columns[ci];
		var size = c1g_getSize(c, (row.style.whiteSpace == ""), afWidth);

		if (param.max == -1)
			param.max = parseInt(row.style.height);
	
		param.max = Math.max(param.max, size[0]);
	}
	
	if (ci == param.lastIndex)
		c1g_rows[param.ri++] = param.max;
	
	return true;
}

function c1g__adjustWidth(p, c, ci, param)
{
	var row = c.parentNode;
	
	if (p.columns[ci].allowAutoSize && !c1g_getattr(row, "fix"))
	{
		var size = c1g_getSize(c, (row.style.whiteSpace == ""), parseInt(p.columns[ci].cols[0].width));
		c1g_columns[ci] = (c1g_columns.length <= ci) ? size[1] : Math.max(c1g_columns[ci], size[1]);
	}
	
	return true;
}

function c1g_getSize(o, wrap, width)
{
	var mCell = c1g_mTable.rows[0].cells[0];
	
	c1g_mTable.rows[0].style.cssText = mCell.style.cssText = "";
	c1g_copyFont(o.parentNode, c1g_mTable.rows[0]);
	c1g_copyFont(o, mCell);
	
	mCell.style.width = (wrap && (width > 0)) ? width + "px" : "";
	mCell.innerHTML = (o.firstChild && o.firstChild.tagName == "DIV") ? o.firstChild.innerHTML : o.innerHTML;

	var cpSpace = c1g_mTable.cellPadding ? parseInt(c1g_mTable.cellPadding) * 2 : 2;
		
	return [mCell.offsetHeight - cpSpace, mCell.offsetWidth - cpSpace];
}

function c1g_copyFont(from, to)
{
	var tmp;
	
	if ((tmp = from.style["fontWeight"]) && to.style["fontWeight"] == "")
		to.style["fontWeight"] = tmp;

	if ((tmp = from.style["fontSize"]) && to.style["fontSize"] == "")
		to.style["fontSize"] = tmp;
		
	if ((tmp = from.style["fontFamily"]) && to.style["fontFamily"] == "")
		to.style["fontFamily"] = tmp;
}