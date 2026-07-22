function C1WebCommandBuilder(data)
{
	this._data = data;

	this._Menu = this._data.Class == 'Menu';
	this._ToolBar  = this._data.Class == 'ToolBar';
	this._TopicBar = this._data.Class == 'TopicBar';
	this._TreeView = this._data.Class == 'TreeView';
	this._TabStrip = this._data.Class == 'TabStrip';
	this._hashEls = [];

	this._createElement = function(tag)
	{
		return document.createElement(tag);
	}

	this._rootElement = document.getElementById(data.ClientID);
	// Workaround for a C1WebSplitter's bug

	if (!this._rootElement)
	{
		var tbls = document.getElementsByTagName('table');
		for(var i=0; i<tbls.length; i++)
		{
			var tbl = tbls[i];
			if (!tbl.id && tbl.timestamp == data.TimeStamp)
			{
				this._rootElement = tbl;
				tbl.id = data.ClientID;
				break;
			}
		}
	}

	if (this._rootElement.rows.length >= 1)
		this._contentRow = this._rootElement.rows[0];
	this._nullWidth = '0%';
	if (navigator.userAgent.toLowerCase().indexOf('msie')==-1)
		this._nullWidth = '1px';
	this._CreateTable = function(wide) {
		var _res = this._createElement("TABLE");
		_res.cellPadding = '0';
		_res.cellSpacing = '0';
		_res.border = '0';
		if (this._GetP(wide,true))
			_res.style.width = '100%';
		return _res;
	}
	this._InsertCell = function (row)
	{
		var _cell = row.insertCell(row.cells.length);
		_cell.vAlign = 'top';
		return _cell;
	}
	this._InsertLastCell = function (row)
	{
		return row.insertCell(row.cells.length);
	}
	this._InsertRow = function(_table)
	{
		return _table.insertRow(_table.rows.length);
	}

	this._MergeStyle = function(st, _style)
	{
		var	ss = _style.split(";");
		if (!st)
			return _style;
		for	(var i = 0;	i <	ss.length; i++)
		{
			if (ss[i])
			{
				var	pair = c1c_splitTwice(ss[i], ":");
				if (st.indexOf(pair[0]+':') == -1)
					st += ss[i] + ';';
			}
		}
		return st;
	}
	this._GetCompoundStyle = function(_controlStyle, _groupStyle, _itemStyle, is)
	{
		var st = '';
		if (_itemStyle)
			st += _itemStyle;
		if (_groupStyle)
			st = this._MergeStyle(st, _groupStyle);
		if (_controlStyle)
			st = this._MergeStyle(st, _controlStyle);
		if (is)
			st = this._MergeStyle(st, is);
		return st;
	}
	this._GetCompoundProperty = function(_cProp, _gProp, _iProp)
	{
		var res = '';
		if (typeof(_iProp) != 'undefined')
			return _iProp;
		else if (typeof(_gProp) != 'undefined')
			return _gProp;
		return _cProp;
	}
	this._GetStyleValue = function(_style, _name)
	{
		if (!_style)
			return "";
		//var r = '(?<='+name+':)(.*?)(?=;)';
		var r = "(^|;)"+_name+':(.*?)(?=;)';
		var m = _style.match(new RegExp(r));
		if (m)
		{
			var	pair = c1c_splitTwice(m[0], ":");
			return pair[1];
		}
		else
			return "";
	}
	this._ApplyStyle = function(el, _style, fo)
	{
		if (!_style)
			return;
		var	ss = _style.split(";");
		for	(var i = 0;	i <	ss.length; i++)
		{
			var	pair = c1c_splitTwice(ss[i], ":");
			if (pair.length	== 2)
			{
				if (typeof(el.style[pair[0]]) != 'undefined' && (!fo || pair[0] == 'fontSize' || pair[0] == 'fontFamily'|| pair[0] == 'color' || pair[0] == 'fontStyle' || pair[0] == 'fontVariant' || pair[0] == 'fontWeight' || pair[0] == 'textAlign'  || pair[0] == 'textDecoration'))
					el.style[pair[0]] = pair[1];
				else if (pair[0] == 'className' && !fo)
					el.className = pair[1];
			}
		}
	}
	this._Content_CreateInternalRepresentationControl = function(row, groupData, data, vert)
	{
		if (this._contentRow)
		{
			var contentCell = this._contentRow.cells[data.ContentIndex];
			this._contentRow.removeChild(contentCell);
			row.appendChild(contentCell);
			this._contentRow.insertCell(data.ContentIndex);
		}
	}
	this._Sep_CreateInternalRepresentationControl = function(body, groupData, data, vert)
	{
		var style = this._GetCompoundStyle(this._data.SeparatorStyle, groupData.SeparatorStyle, data.SeparatorStyle);
		if (style)
		{
			var paddingBottom = this._GetStyleValue(style, "PaddingBottom");
			if (paddingBottom)
				body.style.paddingBottom = paddingBottom;
			var paddingTop = this._GetStyleValue(style, "PaddingTop");
			if (paddingTop)
				body.style.paddingTop = paddingTop;
			var paddingLeft = this._GetStyleValue(style, "paddingLeft");
			if (paddingLeft)
				body.style.paddingLeft = paddingLeft;
			var paddingRight = this._GetStyleValue(style, "paddingRight");
			if (paddingRight)
				body.style.paddingRight = paddingRight;
		}
		if (!vert && typeof(this._data.ItemSize) == 'undefined')
			body.style.height = '100%';
		var innerTable = this._CreateTable(vert);
		body.appendChild(innerTable);
		if (!vert)
		{
			if (typeof(this._data.ItemSize) != 'undefined')
				innerTable.style.height = this._data.ItemSize;
			else if (this._ToolBar)
				innerTable.style.height = '100%';
		}
		var innerRow = innerTable.insertRow(0);
		var innerBody = this._InsertCell(innerRow);

		innerBody.vAlign = 'middle';
		var img = this._createElement('IMG');
		innerBody.appendChild(img);
		img.style.width = '0px';
		img.style.height = '0px';
		img.style.borderWidth = '0px';
		img.width = '';
		img.height = '';
		img.src = this._data.Urls[0];

		var backImageUrl = this._GetStyleValue(style, "BackImageUrl");	  
		if (backImageUrl)
			innerBody.style.backgroundImage = 'url(' + this._data.Urls[backImageUrl] + ')';;

		var size = this._GetStyleValue(style, "BackImageSize");	 
		if (vert)
			innerBody.style.height = size;
		else
			innerBody.style.width = size;
		this._ApplyStyle(body, style);
		var cssClass = this._GetStyleValue(style, "CssClass"); 
		if (!backImageUrl && !cssClass)
		{
			var borderColor = this._GetStyleValue(style, "borderColor");
			var borderStyle = this._GetStyleValue(style, "borderStyle");
			var borderWidth = this._GetStyleValue(style, "borderWidth");
			body.style.borderColor = '';
			if (borderColor)
			{
				body.style.borderColor = '';
				innerBody.style[this._GetCssAttrName("Color", vert)] = borderColor;
			}
			if (borderStyle)
			{
				body.style.borderStyle = '';
				innerBody.style[this._GetCssAttrName("Style", vert)] = borderStyle;
			}
			if (borderWidth)
			{
				body.style.borderWidth = '';
				innerBody.style[this._GetCssAttrName("Width", vert)] = borderWidth;
			}
		}
		// height
		if (!vert)
		{
			var div = this._createElement('DIV');
			innerBody.appendChild(div);
			div.style.overflow = 'hidden';
			div.style.width = '0px';
			div.innerHTML = 'x';
		}

	}

	this._GetCssAttrName = function(part, vert)
	{
		var prefix;
		if (vert)
			prefix = "borderTop";
		else
			prefix = "borderLeft";
		return prefix + part;
	}

	this._Group_ProcessBodyRowStyle = function(row, data, vert)
	{
		if (!vert)
			row.style.height = '100%';
	}
	this._ProcessLabelCell = function(cell, groupData, data, style, header)	   
	{
		cell.unselectable = 'on';
		var wrap = this._GetP(this._GetCompoundProperty(groupData.WrapText, data.WrapText), true);
		if (!wrap || header)
			cell.style.whiteSpace = "nowrap";
		if (data.Text) cell.innerHTML = data.Text;				  
		cell.vAlign = 'middle';
		var ha = this._GetStyleValue(style, "ItemAlign");
		if (ha) cell.align = ha;
		// LabelPadding
		var p;
		p = this._GetStyleValue(style, "LabelPaddingLeft");
		if (p) cell.style.paddingLeft = p;
		p = this._GetStyleValue(style, "LabelPaddingRight");
		if (p) cell.style.paddingRight = p;
		p = this._GetStyleValue(style, "LabelPaddingTop");
		if (p) cell.style.paddingTop = p;
		p = this._GetStyleValue(style, "LabelPaddingBottom");
		if (p) cell.style.paddingBottom = p;
	}
	this._ProcessIconCell = function(cell, groupData, data, style, iw, id)	  
	{
		cell.unselectable = 'on';
		var lit = this._createElement('DIV');
		var img = this._createElement('IMG');
		img.id = id + '_img';
		lit.appendChild(img);
		cell.appendChild(lit);
		if (iw)
		{
			//lit.style.display = "inline-block";
			lit.style.width = iw;
			cell.style.width = iw;
		}
		else
			cell.style.width = this._nullWidth;
		var pos = this._GetStyleValue(style, "ItemImagePosition");
		img.style.borderWidth = '0px';

		//if (data.Class == 'Header')
		//{
		img.style.width = '1px';
		img.style.height = '1px';
		//}
		img.onload = this._onload;


		if (data.ImageUrl)
			img.src = this._data.Urls[data.ImageUrl];
		else
		{
			img.src = this._data.Urls[0];
			img.style.display = 'none';
		}

		var its = this._GetStyleValue(style, "ImageTextSpacing");
		if (its)
			img.style.marginRight = its;
		else if (data.ImageUrl)
			img.style.marginRight = '4px';

	}
	this._ProcessBoundary = function(table, boundaryTable, leftCell, middleCell, rightCell, vert, data, groupData)
	{
		if (vert)
		{
			table.style.width = '100%';
			table.rows[0].style.height = '100%';
		}
		else
			table.style.height = '100%';
		var lburl = this._GetUrl(this._GetStyleValue(data.CurrentStyle, "LeftBorderImageUrl"));
		var mx = data.Class == 'Header' && this._data.MixedBordersMode;
		if (lburl && !(mx && groupData.Index != "0"))
		{
			var img = this._createElement('IMG');
			img.style.borderWidth = '0px';
			img.id = data.ClientID + '_lbi';
			img.style.width = '1px';
			img.style.height = '1px';
			img.onload = this._onload;
			img.src = lburl;
			leftCell.appendChild(img);
			leftCell.style.width = this._nullWidth;
		}
		var rburl;
		if (!mx)
			rburl = this._GetUrl(this._GetStyleValue(data.CurrentStyle, "RightBorderImageUrl"));
		else
		{
			if (!groupData.NextIsActive)
				rburl = this._GetUrl(this._GetStyleValue(data.CurrentStyle, "RightBorderImageUrl"));
			else
				rburl = this._GetUrl(this._GetStyleValue(this._data.ActiveHeaderStyle, "LeftBorderImageUrl"));			  

		}
		if (rburl)
		{
			var img = this._createElement('IMG');
			img.style.borderWidth = '0px';
			img.id = data.ClientID + '_rbi';
			img.onload = this._onload;
			img.style.width = '1px';
			img.style.height = '1px';
			img.src = rburl;
			rightCell.appendChild(img);
			rightCell.style.width = this._nullWidth;
		}


	}
	this._Item_CreateRepresentationControl = function(body, groupData, data, vert, id) 
	{
		this._ProcessItemSpecialSymbolStyle(data, groupData);
		if (data.Class == 'LinkItem' || data.Class == 'Header')
		{
			data.ClientID = id;
			var en = this._GetCompoundProperty(this._data.Enabled, groupData.Enabled, data.Enabled);
			data.IsEnabled = this._GetP(en, true);
			data.Target = this._GetCompoundProperty(data.Target, groupData.Target,this._data.Target);
			var st;
			if (data.Class == 'Header')
			{
				st = this._GetCompoundStyle(this._data.InactiveHeaderStyle, groupData.InactiveHeaderStyle);
				data.CItemStyle = st;
				data.CMouseOverItemStyle = this._GetCompoundStyle(this._data.MouseOverInactiveHeaderStyle, groupData.MouseOverInactiveHeaderStyle, '', data.CItemStyle);
				data.CSelectedItemStyle = this._GetCompoundStyle(this._data.ActiveHeaderStyle, groupData.ActiveHeaderStyle, '', data.CItemStyle);
				data.CMouseOverSelectedItemStyle = this._GetCompoundStyle(this._data.MouseOverActiveHeaderStyle, groupData.MouseOverActiveHeaderStyle, '', data.CItemStyle);

				if (!data.IsEnabled)
				{
					st = this._GetCompoundStyle(this._data.DisabledHeaderStyle, groupData.DisabledHeaderStyle, '', st);
					data.CDisabledItemStyle = st;
					data.CItemStyle = st;
				}	 
				else if (data.Selected)
					st = data.CSelectedItemStyle;
			}
			else
			{
				st = this._GetCompoundStyle(this._data.ItemStyle, groupData.ItemStyle, data.ItemStyle);
				data.CItemStyle = st;
				data.CMouseOverItemStyle = this._GetCompoundStyle(this._data.MouseOverItemStyle, groupData.MouseOverItemStyle, data.MouseOverItemStyle, data.CItemStyle);
				data.CSelectedItemStyle = this._GetCompoundStyle(this._data.SelectedItemStyle, groupData.SelectedItemStyle, data.SelectedItemStyle, data.CItemStyle);
				data.CMouseOverSelectedItemStyle = this._GetCompoundStyle(this._data.MouseOverSelectedItemStyle, groupData.MouseOverSelectedItemStyle, data.MouseOverSelectedItemStyle, data.CItemStyle);
				if (this._Menu && this._GetP(data.Level,1) > 0)
				{	 
					st = this._GetCompoundStyle(this._data.SubMenuItemStyle, groupData.SubMenuItemStyle, data.SubMenuItemStyle, st);
					data.CItemStyle = st;
					data.CMouseOverItemStyle = this._GetCompoundStyle(this._data.SubMenuMouseOverItemStyle, groupData.SubMenuMouseOverItemStyle, data.SubMenuMouseOverItemStyle, data.CMouseOverItemStyle);
					data.CSelectedItemStyle = this._GetCompoundStyle(this._data.SubMenuSelectedItemStyle, groupData.SubMenuSelectedItemStyle, data.SubMenuSelectedItemStyle, data.CSelectedItemStyle);
					data.CMouseOverSelectedItemStyle = this._GetCompoundStyle(this._data.SubMenuMouseOverSelectedItemStyle, groupData.SubMenuMouseOverSelectedItemStyle, data.SubMenuMouseOverSelectedItemStyle, data.CMouseOverSelectedItemStyle);
				}
				if (this._Menu)
				{
					var checkImg;
					var o = this._GetP(data.Level,1) == 0 ? this._data : groupData;
					if (!this._GetP(o.AllowMultipleSelect, true) && data.SpecialSymbolStyle.RadioMarkImageUrl)
						checkImg = data.SpecialSymbolStyle.RadioMarkImageUrl;
					else if(data.SpecialSymbolStyle.CheckMarkImageUrl)
						checkImg = data.SpecialSymbolStyle.CheckMarkImageUrl;
					if (checkImg && !(this._GetStyleValue(data.CItemStyle, "ImageUrl") || this._GetStyleValue(data.CMouseOverItemStyle, "ImageUrl") || this._GetStyleValue(data.CSelectedItemStyle, "ImageUrl") || this._GetStyleValue(data.CMouseOverSelectedItemStyle, "ImageUrl")))
					{
						data.CSelectedItemStyle += 'ImageUrl:'+checkImg+';';
						data.CMouseOverSelectedItemStyle += 'ImageUrl:'+checkImg+';';
					}
				}
				if (!data.IsEnabled)
					st = this._GetCompoundStyle(this._data.DisabledItemStyle, groupData.DisabledItemStyle, data.DisabledItemStyle, st);
				else if (data.Selected)
					st = data.CSelectedItemStyle;
			}
			data.CurrentStyle = st;
			data.Hash = this.getHash(vert,st,data,groupData);
			data.ImageUrl = this._GetStyleValue(st, "ImageUrl");

			var res;
			var iipos = this._GetStyleValue(st, "ItemImagePosition");
			data.TextOnly = iipos == 'TextOnly';
			data.ImageOnly = iipos == 'ImageOnly';
			var elToClone = this.getFromHashTable(data.Hash);
			if (elToClone)
			{
				res = this.cloneItem(elToClone, id, data);
				body.appendChild(res);	  
				return res;
			}
			res = this._CreateTable();
			body.appendChild(res);
			res.id = id + '_bt';
			if (data.IsEnabled && !this._data.firstLinkItem)
				this._data.firstLinkItem = res;
			var tr = res.insertRow(0);
			var lc = this._InsertCell(tr);
			var mc = this._InsertCell(tr);
			var rc = this._InsertCell(tr);


			//C1WebItemBase.ProcessBoundary
			if (vert)
			{
				res.style.width = '100%';
				//tr.style.height = '100%';
			}
			else
			{
				//??? res.style.height = '100%';
			}

			lc.style.height = '100%';
			mc.style.height = '100%';
			rc.style.height = '100%';
			mc.style.width = '100%';
			rc.style.width = this._nullWidth;
			lc.style.width = this._nullWidth;
			mc.vAlign = 'middle';
			mc.id = id + '_mbc';
			lc.vAlign = 'middle';
			rc.vAlign = 'middle';

			var url =  this._GetStyleValue(st, "BackImageUrl");			 
			if (url)
				mc.style.backgroundImage = 'url('+this._data.Urls[url]+')';

			// C1WebItemBase.ProcessTableStyle
			res.style.width = '100%';


			var it = this._CreateTable();
			mc.appendChild(it);
			//it.style.width = '100%';
			//if (data.Class != 'Header' || this.TabPos == 'Top' ||	 this.TabPos == 'Bottom' )
			//	  it.style.height = '100%';

			var ir = it.insertRow(0);
			//if (data.Class == 'Header' && this.TabPos != 'Top' &&	 this.TabPos != 'Bottom')
			//	  ir.style.height = '100%';

			var ic = this._InsertCell(ir);
			ic.id = id;

			this._ProcessBoundary(it, res, lc, mc, rc, vert, data, groupData);
			if (data.ToolTip)
				ic.title = data.ToolTip;
			if (data.Class != 'Header')
			{
				var p = this._GetCompoundProperty(this._data.ItemPadding, groupData.ItemPadding);
				if (p)
					ic.style.padding = p;
			}

			var it1 = this._CreateTable();
			ic.appendChild(it1);
			it1.style.height = '100%';
			it1.style.width = '100%';
			ic.vAlign = 'top';

			for(var r=0; r<3; r++)
			{
				ir = it1.insertRow(r);
				ir.style.height = '0px';
				for(var c=0; c<3; c++)
				{
					var ic1 = this._InsertCell(ir);
					if (r != 1)
						ic1.style.height = '0%';
					ic1.vAlign = 'top';
					if (c == 0)
						ic1.align = 'left';
					else if (c == 2)
						ic1.align = 'right';
				}
			}
			if (!data.TextOnly)
			{
				var i_cell = it1.rows[1].cells[0];
				if (iipos == 'Far')
					i_cell = it1.rows[1].cells[2];
				else if (iipos == 'Top')
					i_cell = it1.rows[0].cells[1];
				else if (iipos == 'Bottom')
					i_cell = it1.rows[2].cells[1];
				var iw;
				if (this._Menu && this._GetP(data.Level,1) > 0)
				{
					iw = this._GetCompoundProperty(this._data.SubMenuIconBarWidth, groupData.IconBarWidth, data.IconBarWidth);
					if (!iw)
						iw = this._data.IconBarWidth;
				}
				else
					iw = this._GetCompoundProperty(this._data.IconBarWidth, groupData.IconBarWidth, data.IconBarWidth);
				if (iw)
					i_cell.style.width =  iw;
				else 
					i_cell.style.width =  '0%';
				this._ProcessIconCell(i_cell, groupData, data, st, iw, id);
			}
			mc = it1.rows[1].cells[1];
			if (!data.ImageOnly)
			{
				this._ProcessLabelCell(mc, groupData, data, st, data.Class == 'Header');
				mc.id = id+'_txt';
			}
			this._ApplyStyle(ic, st);
			this._ApplyStyle(it1, st, true);
			this._Item_ProcessTableStyle(res, vert);
			// C1WebToolBarItem_InternalPostProcessInnerTable
			if (this._ToolBar)
				this._ToolBarItem_InternalPostProcessInnerTable(it1, data, vert, id);
			else if (data.Class == 'Header')
				this._Header_InternalPostProcessInnerTable(it1, data, vert, id);
			else if (this._Menu)
				this._MenuItem_InternalPostProcessInnerTable(it1, groupData, data, vert);	 
			else if (this._TreeView)
				this._TreeItem_InternalPostProcessInnerTable(it1, groupData, data, vert);	 
			this._Shortcut_InternalPostProcessInnerTable(it1, data, vert, id);
			if (!data.CheckedCheckBox)
				this.addElToHash(data.Hash, res, id);
			return res;
		}
		else if (data.Class == 'Separator')
		{
			var res = this._CreateTable(vert);
			body.appendChild(res);
			var row = res.insertRow(0);
			var cell = this._InsertCell(row);
			this._Sep_CreateInternalRepresentationControl(cell, groupData, data, vert);
			this._Item_ProcessTableStyle(res, vert);
			return res;
		}
		else if (data.Class == 'ContentItem')
		{
			var res = this._CreateTable(vert);
			body.appendChild(res);
			var row = res.insertRow(0);
			this._Content_CreateInternalRepresentationControl(row, groupData, data, vert);
			this._Item_ProcessTableStyle(res, vert);
			return res;
		}

	}
	this._TreeItem_InternalPostProcessInnerTable = function(it, groupData, data, vert)
	{
		var row = it.rows[0];
		var cellBefore = row.firstChild;
		if (data.ShowCheckBox)
		{
			var cell_cbx = row.insertCell(0);
			cellBefore = cell_cbx;
			cell_cbx.rowSpan = 3;
			cell_cbx.style.align = 'left';
			cell_cbx.vAlign = 'middle'; 
			cell_cbx.style.width = '1px';
			var cbx = this._createElement('INPUT');
			cbx.type = 'checkbox';
			cell_cbx.appendChild(cbx);
			var _checked = this._GetP(data.Selected, false);
			if (_checked)
			{
				cbx.checked = true;
				data.CheckedCheckBox = true;
			}
			if (!this._GetP(data.IsEnabled, true))
				cbx.setAttribute('disabled', 'disabled');
			cbx.onclick = SetCheckboxClicked;
			cbx.id = data.ClientID + '_cbx';

		}
		var indCell = this._createElement('TD');
		indCell.rowSpan = 3;
		indCell.style.width = this._nullWidth;
		indCell.align = 'right';
		indCell.vAlign = 'middle';
		var indTxt = '&nbsp;';
		var style = data.SpecialSymbolStyle;
		var indUrl = style.NoExpandNodeImageUrl; 
		var indId = data.ClientID + '_ti';
		if (data.NestedGroup || data.ActualPopulateOnDemand)
			if (data.ActualPopulateOnDemand || !this._GetP(data.NestedGroup.ActualActive, true))
			{
				indUrl = style.CollapsedNodeImageUrl;
				indTxt = "+";
			}
			else
			{
				indUrl = style.ExpandedNodeImageUrl;
				indTxt = "-";
			}
		if (indUrl)
		{
			var img = this._createElement('IMG');
			img.id = indId;
			img.onload = this._onload;
			img.style.width = '16px';
			img.style.height = '16px';
			img.src = this._GetUrl(indUrl); 
			img.style.borderWidth = '0px';

			if (this._data.ShowLines && this._GetP(data.Level, 1) > 0)
			{
				var indLine = row.insertCell(0);
				indLine.rowSpan = 3;
				indLine.style.width = this._nullWidth;
				indLine.align = 'left';
				indLine.vAlign = 'bottom';

				var indLineImg = this._createElement('IMG');
				indLineImg.style.borderWidth = '0px';
				indLineImg.src = this._GetUrl(style.HorizontalLineImageUrl);
				indLine.appendChild(indLineImg);
			}

			indCell.appendChild(img);
			img.onclick = SetPlusMinusClicked;
		}
		else
		{
			var lc = this._createElement('SPAN');
			lc.id = indId;
			lc.style.width = '20px';
			lc.style.textAlign = 'center';
			lc.innerHTML = indTxt;
			indCell.appendChild(lc);
		}
		row.insertBefore(indCell, cellBefore);
	}
	this._MenuItem_InternalPostProcessInnerTable = function(it, groupData, data, vert)
	{
		var smm = this._GetP(this._data.SubMenuMark, 'Yes');
		if (smm == 'No' || (!(data.SubMenu || smm == 'Yes') || !vert))
			return;
		var row = it.rows[0];
		var cellInd;
		if (this._GetP(this._data.HorzPopupDirection, 'LeftToRight') == 'LeftToRight')
			cellInd = 3;
		else
			cellInd = 0;
		var indCell = row.insertCell(cellInd);
		indCell.rowSpan = 3;
		indCell.style.width = this._nullWidth;
		indCell.align = 'right';
		indCell.vAlign = 'middle';
		var indUrl; 
		var indTxt;
		indUrl	= this._GetUrl(this._data.SpecialSymbolStyle.SubMenuMarkImageUrl);
		indTxt = groupData.SpecialSymbolStyle.SubMenuMarkText;
		if (!indTxt && !indUrl)
		{
			indUrl = this._GetUrl(this._data.SubMenuMarkImageUrl);
		}
		if (indUrl)
		{
			var img = this._createElement('IMG');
			indCell.appendChild(img);
			img.style.borderWidth = '0px';
			{
				img.onload = this._onload;
				img.style.width = '10px';
			}
			if (!data.SubMenu)
				img.style.visibility = 'hidden';
			img.src = indUrl;
			img.alt = "Expand " + (typeof(it.innerText) == 'undefined' ? it.textContent : it.innerText);
		}
		else
		{
			if (data.SubMenu)
				indCell.innerHTML = indTxt;
			else
				indCell.innerHTML = "<span style=\"overflow:hidden;height:0px;visibility:hidden;\">_</span>";
		}
	}
	this._ToolBarItem_InternalPostProcessInnerTable = function(it, data, vert, id)
	{
		var row = it.rows[0];
		if (data.HasDropDownButton && !vert)
		{
			var _cell_cbx = this._InsertCell(row);
			_cell_cbx.rowSpan = 3;
			_cell_cbx.align = 'left';
			_cell_cbx.vAlign = 'middle';
			_cell_cbx.style.width = '1px';
			_cell_cbx.setAttribute('unselectable', 'on');

			var _img = this._createElement('IMG');
			_cell_cbx.appendChild(_img);
			_img.style.width = '9px';
			_img.style.height = '16px';
			_img.style.borderWidth = '0px';
			_img.src = this._data.Urls[data.DropDownButtonImageUrl];
			if (data.IsEnabled)
			{
				_cell_cbx.onclick = this._dropDownButtonFunc;
				_cell_cbx.id = id + '_dropBtn';
				_cell_cbx._dropDownContextMenuId = data.DropDownContextMenuId;
			}
		}
		var indCell = row.insertCell(0);
		indCell.rowSpan = 3;
		indCell.style.width = this._nullWidth;
		indCell.align = 'right';
		indCell.vAlign = 'middle';
	}
	this._Shortcut_InternalPostProcessInnerTable = function(it, data, vert, id)
	{
		var row = it.rows[0];
		if (data.KeyboardShortcut && this._GetP(this._data.ShowKeyboardShortcuts, true))
		{
			var idx = this._TreeView ? 4 : 3;
			var _cell_cbx = row.insertCell(idx);
			_cell_cbx.rowSpan = 3;
			_cell_cbx.align = 'right';
			_cell_cbx.vAlign = 'middle';
			_cell_cbx.innerHTML = data.KeyboardShortcut;			
		}
	}
	this._Header_InternalPostProcessInnerTable = function(it, data, vert, id)
	{
		var row = it.rows[0];
		var exStyle;
		var colStyle;
		if (data.IsEnabled)
		{
			exStyle = data.CSelectedItemStyle;
			colStyle = data.CItemStyle;
		}
		else
		{
			exStyle = data.CDisabledItemStyle;
			colStyle = exStyle;
		}

		var iip =  this._GetStyleValue(exStyle, "ItemImagePosition");		 
		var cellind;
		if (iip && iip == 'Far')
			cellInd = 0;
		else
			cellInd = 3;

		var indCell = row.insertCell(cellInd);
		indCell.rowSpan = 3;
		indCell.style.width = this._nullWidth;
		indCell.align = 'right';
		indCell.vAlign = 'middle';

		var img = this._createElement('IMG');
		indCell.appendChild(img);
		img.style.borderWidth = '0px';
		img.id = id + '_ind';

		var indUrl;	   
		if (data.Selected)		  
			indUrl = this._GetStyleValue(exStyle, "IndicatorUrl"); 
		else
			indUrl = this._GetStyleValue(colStyle, "IndicatorUrl"); 

		if (!indUrl)
		{
			indUrl = 0;
			img.style.height = '0%';
			img.style.width = this._nullWidth;

		}
		else
		{
			img.onload = this._onload;
			img.style.height = '1px';
			img.style.width = '25px';
		}

		img.src = this._GetUrl(indUrl);
	}

	this._Item_ProcessTableStyle = function(res, vert)
	{
		res.style.width = '100%';
	}

	this._ProcessBodyStyle = function(cell, data, vert)
	{
		// C1WebCustomGroup.ProcessBodyStyle
		if (!vert)
			cell.style.height = '100%';
		var gp = this._GetCompoundProperty(this._data.GroupPadding, data.GroupPadding);
		if (gp)
			cell.style.padding = gp;
	}
	this._CreateItemSpacing = function(item,vert,isp)
	{
		var st;
		if (vert)
			st = "height";
		else
			st = "width";
		var res = this._createElement('DIV');
		res.style.overflow = 'hidden';
		res.style[st] = isp;

		if (vert && (this._rootElement.style.textDecorationOverline ||
					 this._rootElement.style.textDecorationUnderline ||
					 this._rootElement.style.textDecorationLineThrough))
			res.innerHTML = '';
		else
			res.innerHTML = '&nbsp;';
		return res;
	}

	this._Item_AddRepresantationNestedGroup = function(cell, group, item, vert, id, level)
	{
		if (item.SubMenu)
			this._Group_CreateRepresentationControl(cell, item.SubMenu, 0, this._GetP(item.Level,0), item.ClientID);
		if (item.ActualPopulateOnDemand)
		{
			item.NestedGroup = new Object();
			item.NestedGroup.WaitControl = true;
			item.NestedGroup.ActualActive = false;
		}

		if (item.NestedGroup)
		{
			if (item.ShowCheckBox)
				item.NestedGroup.ShowCheckBoxes = true;
			var table = this._CreateTable();
			cell.appendChild(table);
			var row = this._InsertRow(table);
			var cell1 = this._InsertCell(row);
			var cell2 = this._InsertCell(row);

			if (this._data.ShowLines)
			{
				var style = group.SpecialSymbolStyle;
				var indUrl = this._GetUrl(style.NoExpandNodeImageUrl); 
				var vertUrl = this._GetUrl(style.VerticalLineImageUrl); 
				cell1.style.width = '10px';
				cell1.style.backgroundRepeat = 'repeat-y';
				cell1.style.backgroundPosition = 'bottom right';
				cell1.style.backgroundImage = 'url('+vertUrl+')';

			}
			else
				cell1.style.width = '20px';

			this._Group_CreateRepresentationControl(cell2, item.NestedGroup, 0, this._GetP(item.Level,0), item.ClientID);
		}

	}
	this._Group_CreateItemsRepresentationControls = function(row, data, vert, group_id) 
	{
		var vis = 0;
		var isp = this._GetCompoundProperty(this._data.ItemSpacing, data.ItemSpacing);
		//if (typeof(data.Items) == 'undefined')
		//	  return;
		this._Group_ProcessBodyRowStyle(row, data, vert);
		if (vert)
		{
			var cell = this._InsertCell(row);
			this._ProcessBodyStyle(cell, data, vert);
			if (this._data.ExpandEffect && this._TopicBar)
			{
				div = document.createElement('div');
				div.id = row.id+'_expand';
				cell = cell.appendChild(div);
				div = document.createElement('div');
				cell = cell.appendChild(div);
			}
			if (typeof(data.Items) != 'undefined')
			{
				for(var i=0;i<data.Items.length;i++) {
					var item = data.Items[i];
					if (data.ShowCheckBoxes)
						item.ShowCheckBox = true;
					if (typeof(item.Visible) == 'undefined' || item.Visible)
					{
						if (vis > 0 && typeof(isp) != 'undefined')
						{
							var c = this._CreateItemSpacing(item,vert,isp);
							if (c)
								cell.appendChild(c);
						}
						var id = group_id + '_i'+item.Index; 
						this._Item_CreateRepresentationControl(cell, data, item, vert, id);
						this._Item_AddRepresantationNestedGroup(cell, data, item, vert, id);
						vis++;
					}
				}
			}
			else
			{
				if (this._rootElement.style.textDecorationOverline ||
					this._rootElement.style.textDecorationUnderline ||
					this._rootElement.style.textDecorationLineThrough)
					cell.innerHTML = '<br/>';
				else
					cell.innerHTML = '&nbsp;';
			}
		}
		else
		{
			if (typeof(data.Items) != 'undefined')
				for(var i=0;i<data.Items.length;i++) {
					var item = data.Items[i]; 
					if (typeof(item.Visible) == 'undefined' || item.Visible)
					{
						var cell = this._InsertCell(row);
						this._ProcessBodyStyle(cell, data, vert);

						var id = group_id + '_i'+i; 
						this._Item_CreateRepresentationControl(cell, data, item, vert, id);
						this._Item_AddRepresantationNestedGroup(cell, data, item, vert, id);
						if (vis > 0 && typeof(isp) != 'undefined')
						{
							if (vert)
								cell.style.paddingTop = isp;
							else
								cell.style.paddingLeft = isp;
						}

						vis++;
					}
				}
		}
		// C1WebGroupHeader.CreateItemsRepresentationControls
		if (this._TopicBar || this._TabStrip || data.WaitControl)
		{
			this._Group_CreateWaitCallbackControl(row, data, group_id, this._GetP(data.ActualPopulateOnDemand, false) && !this._GetP(data.ActualActive, true));
		}
	}
	this._Group_CreateWaitCallbackControl = function(bodyRow, data, id, visible)
	{
		if (visible)
		{
			while (bodyRow.firstChild)
				bodyRow.removeChild(bodyRow.firstChild);
		}
		var cell; 
		if (this._TreeView)
		{
			cell = this._InsertCell(bodyRow);
			this._ProcessBodyStyle(cell, data, true);
			cell.align = 'left';
			cell.style.width = '100%';
		}
		else
		{
			cell = bodyRow.firstChild.appendChild(document.createElement('DIV'));
			this._ProcessBodyStyle(cell, data, true);
			cell.align = 'center';
		}
		cell.id = id + '_cb';

		if (!this._data.CallbackWaitControlID)
		{
			cell._dontClone = true;
			var waitimg = this._GetUrl(this._GetP(this._data.CallbackWaitImageUrl, 1));
			var img = this._createElement('IMG');
			cell.appendChild(img);
			img.style.borderWidth = 0;
			img.src = waitimg;
			data.CallbackWaitControlID = cell.id;
		}
		else
			data.CallbackWaitControlID = this._data.CallbackWaitControlID;

		if (!visible && !this._TreeView)
			cell.style.display = 'none';

	}
	this._ProcessSpecialSymbolStyle = function(data)
	{
		if (!this._data.SpecialSymbolStyle)
			this._data.SpecialSymbolStyle = new Object();
		var cst = this._data.SpecialSymbolStyle;
		if (!data.SpecialSymbolStyle)
			data.SpecialSymbolStyle = cst;
		var gst = data.SpecialSymbolStyle;
		this._ProcessSSS(gst, cst);

	}
	this._ProcessSSS = function(gst, cst)
	{
		if (!gst.CheckMarkImageUrl)
			gst.CheckMarkImageUrl = cst.CheckMarkImageUrl;
		if (!gst.RadioMarkImageUrl)
			gst.RadioMarkImageUrl = cst.RadioMarkImageUrl;
		if (!gst.SubMenuMarkImageUrl)
			gst.SubMenuMarkImageUrl = cst.SubMenuMarkImageUrl;
		if (!gst.SubMenuMarkText)
			gst.SubMenuMarkText = cst.SubMenuMarkText;
		if (!gst.CollapsedNodeImageUrl)
			gst.CollapsedNodeImageUrl = cst.CollapsedNodeImageUrl;
		if (!gst.NoExpandNodeImageUrl)
			gst.NoExpandNodeImageUrl = cst.NoExpandNodeImageUrl;
		if (!gst.ExpandedNodeImageUrl)
			gst.ExpandedNodeImageUrl = cst.ExpandedNodeImageUrl;
		if (!gst.VerticalLineImageUrl)
			gst.VerticalLineImageUrl = cst.VerticalLineImageUrl;
		if (!gst.HorizontalLineImageUrl)
			gst.HorizontalLineImageUrl = cst.HorizontalLineImageUrl;
	}
	this._ProcessItemSpecialSymbolStyle = function(data, _gdata)
	{
		if (!_gdata.SpecialSymbolStyle)
			_gdata.SpecialSymbolStyle = new Object();
		var cst = _gdata.SpecialSymbolStyle;
		if (!data.SpecialSymbolStyle)
			data.SpecialSymbolStyle = cst;
		var gst = data.SpecialSymbolStyle;
		this._ProcessSSS(gst, cst);
	}
	this._Group_CreateRepresentationControl = function(cell, data, index, level, parId)
	{
		this._ProcessSpecialSymbolStyle(data);
		var vert = !(this._ToolBar && (typeof(this._data.Layout) == "undefined" || this._data.Layout == 'Horizontal'));
		var res = this._CreateTable(vert && !this._Menu);
		var row = res.insertRow(res.rows.lenght);
		with (res) {
			if (this._TopicBar || this._TabStrip || this._ToolBar)
				id = parId + '__g' + index;
			else
				id = parId + '_g' + index;
			data.ClientID = id;
			row.id = id + '_br';
		}
		if (this._Menu)
		{
			res.style.display = "none";
			data.IsActive = false;
		}
		if (this._TopicBar && !this._GetP(data.ActualActive, true))
		{
			row.style.display = "none";
			data.IsActive = false;
		}
		else if (this._TabStrip && !this._GetP(data.ActualActive, true))
		{
			data.IsActive = false;
			res.style.display = "none";
		}
		else if (this._TreeView	 && !this._GetP(data.ActualActive, true))
		{
			data.IsActive = false;
			res.style.display = "none";
		}
		var div = null;
		if (this._data.ExpandEffect && this._data.ExpandEffect != 'Fade' && !this._TopicBar)
		{
			div = document.createElement('div');
			div.id = res.id+'_expand';
		}

		if (!div)
		{
			if (this._Menu)
				this._rootElement.parentNode.appendChild(res);
			else
				cell.appendChild(res);
		}
		else
		{
			if (this._Menu)
				this._rootElement.parentNode.appendChild(div);
			else
				cell.appendChild(div);
			div.appendChild(res);
		}
		with (res) {
			if (data.ToolTip)
				title = data.ToolTip;
			var st;
			data.IsActive = true;
			this._Group_ProcessTableStyle(res, data, vert);

			//if (this.Class == 'TopicBar' && typeof(this._data.ShowGroupHeaders) == 'undefined')
			//{
			//	  var headerRow = res.insertRow(res.rows.lenght);
			//	  var headerCell = this._InsertCell(row);
			//	  headerCell.valign = 'top';
			//}


			if (!this._TabStrip)
				data.BodyRowClientID = id + '_br';
			else
				data.BodyRowClientID = id;

			row.style.height = '100%';
			// HasHeaderRow
			if (this._TopicBar && this._GetP(this._data.ShowGroupHeaders, true))
			{
				var hr = res.insertRow(0);
				var hc = this._InsertCell(hr);
				this._ProcessHeaderRow(hr);
				this._ProcessHeaderCell(hc, data, index);
			}

			this._Group_CreateItemsRepresentationControls(row, data, vert, id);
		}
		if (!this._GetP(data.Enabled, true))
			res._disabled = true;
		return res;
	}	
	this._ProcessHeaderRow = function(row)
	{
	}
	this._ProcessHeaderCell = function(cell, gdata, index)
	{
		if (this._TopicBar)
		{
			var header = this._Header_Create(cell, gdata, index);
			this._ProcessHeaderControlStyle(header);
		}
	}
	this._Header_Create = function(cell, gdata, index)
	{
		var data = {Class: 'Header', Selected: this._GetP(gdata.ActualActive, true), Text: this._GetP(gdata.Text, '')};
		var id = this._data.ClientID + '_h_' + index + '_0';
		gdata.header = data;
		var vert = true;
		if (this.TabPos == 'Top' || this.TabPos == 'Bottom')
			vert = false;
		return this._Item_CreateRepresentationControl(cell, gdata, data, vert, id)	   ;
	}
	this._ProcessHeaderControlStyle = function(header)
	{
	}
	this._CreateHeaderContent = function(body, data)
	{
		var result = this._CreateTable(this.AllHeadersInSingleCell);
		body.appendChild(result);
		var row = this._InsertRow(result);
		row.style.height = '100%';
		this._CreateRepresentationHeaders(row);
	}
	this._CreateRepresentationHeaders = function(bodyRow)
	{
		with (this._data)
		{
			if (this.AllHeadersInSingleCell)
			{
				var cell = this._InsertCell(bodyRow);
				for (var i=0;i<Groups.length;i++)
				{
					var group = Groups[i];
					group.NextIsActive = ((i+1) < Groups.length) && this._GetP(Groups[i+1].ActualActive, true);
					if (typeof(group.Visible) == "undefined" || group.Visible)
						this._Header_Create(cell, group,i);
				}
			}
			else
			{
				for (var i=0;i<Groups.length;i++)
				{
					var group = Groups[i];
					group.NextIsActive = ((i+1) < Groups.length) && this._GetP(Groups[i+1].ActualActive, true);
					if (typeof(group.Visible) == "undefined" || group.Visible)
					{
						var cell = this._InsertCell(bodyRow);
						cell.style.height = '100%';
						this._Header_Create(cell, group,i);
					}
				}
			}
		}
	}
	this._Group_ProcessTableStyle = function(table, data, vert)
	{

		if (!vert)
		{
			table.style.styleFloat = 'left';
			table.style.cssFloat = 'left';
		}

		var st;
		if (this._Menu)
			st = this._GetCompoundStyle(this._data.SubMenuStyle, data.GroupStyle);	
		else if (this._GetP(data.Enabled, true))
			st = this._GetCompoundStyle(this._data.GroupStyle, data.GroupStyle);
		else
			st = this._GetCompoundStyle(this._data.DisabledGroupStyle, data.DisabledGroupStyle);

		if (this._TabStrip && !table.style.width)
			table.style.width = '100%';

		this._ApplyStyle(table, st);
		if (!this._GetP(data.ActualActive, true) && this._TopicBar)
			table.style.height = '';

		if (this._data.HideTabSideGroupBorder)
		{

			table.style['border'+this.TabPos+'Style'] = "";
			table.style['border'+this.TabPos+'Width'] = "";
			table.style['border'+this.TabPos+'Color'] = "";
		}

		data.Height = this._GetStyleValue(st, 'height');


		var backurl = this._GetUrl(this._GetStyleValue(st, 'BackImageUrl'));
		if (backurl)
			table.style.backgroundImage = 'url(' + backurl + ')';
		if (this._Menu && !this._GetP(vert, true))
		{
			table.style.styleFloat = 'left';
			table.style.cssFloat = 'left';
		}

		if (data.GroupSpacing)
		{
			if (vert)
				table.style.marginTop = data.GroupSpacing;
			else
				table.style.marginLeft = data.GroupSpacing;
		}

	}

	this._ProcessTableStyle = function(table, vert)
	{

		if (!vert)
		{
			table.style.styleFloat = 'left';
			table.style.cssFloat = 'left';
		}
		var st;
		st = this._data.GroupStyle;	 
		this._ApplyStyle(table, st);

		var backurl = this._GetUrl(this._GetStyleValue(st, 'BackImageUrl'));
		if (backurl)
			table.style.backgroundImage = 'url(' + backurl + ')';
	}

	this._CustomTree_ProcessBodyRowStyle = function(bodyRow)
	{
	}
	this.CustomTree_ProcessBodyStyle = function(body, vert)
	{
		if (this._Menu && !vert)
			body.style.height = '100%';
	}

	this._CustomTree_CreateItemsRepresentationControls = function(bodyRow, vert)
	{
		var gdata = new Object();
		gdata.WrapText = vert ? true : false;
		gdata.SpecialSymbolStyle = new Object();
		this._ProcessSpecialSymbolStyle(gdata);
		this._CustomTree_ProcessBodyRowStyle(bodyRow);
		if (vert)
		{
			var cell = this._InsertCell(bodyRow);
			this.CustomTree_ProcessBodyStyle(cell,vert);
			if (this._data.Items)
				for(var i=0;i<this._data.Items.length;i++)
				{
					var item = this._data.Items[i];
					item.Level = 0;
					if (!item.ShowCheckBox)
						item.ShowCheckBox = this._data.ShowCheckBoxes;
					var id = this._data.ClientID + '_int_i'+i;
					this._Item_CreateRepresentationControl(cell, gdata, item, vert, id);
					this._Item_AddRepresantationNestedGroup(cell, gdata, item, vert, id);
				}
		}
		else
		{
			if (this._data.Items)
				for(var i=0;i<this._data.Items.length;i++)
				{
					var item = this._data.Items[i];
					item.Level = 0;
					var cell = this._InsertCell(bodyRow);
					var id = this._data.ClientID + '_int_i'+i;
					this.CustomTree_ProcessBodyStyle(cell);
					this._Item_CreateRepresentationControl(cell, gdata, item, vert, id);
					this._Item_AddRepresantationNestedGroup(cell, gdata, item, vert, id);
				}
		}
	}
	this._CustomTree_CreateControlContent = function(body) 
	{
		var vert = (this._TreeView || this._GetP(this._data.Layout, 'Vertical') == 'Vertical');
		var result = this._CreateTable(vert);
		body.appendChild(result);
		result.id = this._data.ClientID + '_int';
		var row = this._InsertRow(result);
		row.id = result.id + '_br';
		row.style.height = '100%';
		this._ProcessTableStyle(result, vert);
		this._CustomTree_CreateItemsRepresentationControls(row, vert);
		if (this._data.Padding)
			body.style.padding = this._data.Padding;
	}

	this._CreateControlContent = function (){ 
		// C1WebCommandBase.CreateChildControls
		var row = this._InsertRow(this._rootElement);
		this._rootRow = row;
		row.style.height = '100%';
		row.style.width = '100%';
		var cell = this._InsertCell(row);
		cell.style.height = '100%';
		cell.style.width = '100%';
		cell.vAlign = 'top';
		//C1WebCommandBase.ProcessControlStyle
		if (typeof(this._data.Padding) == 'undefined')
			cell.style.padding = '0px';
		else
			cell.style.padding = this._data.Padding;
		if (this._data.EnableDragDrop)
		{
			this._data.SortableElement = cell;
			cell.id = this._data.ClientID + '_srt';
		}

		if (this._TabStrip)
		{
			this.TabPos = this._GetP(this._data.TabPosition, 'Top');
			this.AllHeadersInSingleCell = (this.TabPos == 'Left' || this.TabPos == 'Right');
			var table = this._CreateTable(true);
			cell.appendChild(table);	
			var headerRow;
			var bodyRow;
			var headerCell;
			var bodyCell;
			var sep;
			with (this._data)
			{
				if (this._GetP(this._data.ShowTabs, true))
				{
					if (this.TabPos == 'Top')
					{
						headerRow = table.insertRow(0);
						bodyRow = table.insertRow(1);
						headerCell = headerRow.insertCell(0);
						//sep = headerRow;
					}
					if (this.TabPos == 'Bottom')
					{
						bodyRow = table.insertRow(0);
						headerRow = table.insertRow(1);
						headerCell = headerRow.insertCell(0);
						//sep = headerRow;
					}
					if (this.TabPos == 'Left')
					{
						bodyRow = table.insertRow(0);
						headerCell = bodyRow.insertCell(0);
						//sep = headerCell;
					}
					if (this.TabPos == 'Right')
					{
						bodyRow = table.insertRow(0);
						bodyCell = this._InsertCell(bodyRow);
						headerCell = this._InsertCell(bodyRow);
						//sep = headerCell;
					}
					sep = headerCell;
					headerCell.vAlign = 'top';
					//headerCell.style.height = '100%';
					var surl = this._GetUrl(this._data.SeparatorInactiveImageUrl);
					if (surl)
					{
						var pos;
						var repeat;
						if (this.TabPos == 'Top')
						{
							pos = 'bottom';
							repeat = 'x';
						}
						else if (this.TabPos == 'Bottom')
						{
							pos = 'top';
							repeat = 'x';
						}
						else if (this.TabPos == 'Left')
						{
							pos = 'right';
							repeat = 'y';
						}
						else
						{
							pos = 'left';
							repeat = 'y';
						}
						sep.style.backgroundImage = 'url('+surl+')';
						sep.style.backgroundPosition = pos;
						sep.style.backgroundRepeat = "repeat-"+repeat;
					}
				}
				else
					bodyRow = table.insertRow(0);
				if (!bodyCell)
					bodyCell = this._InsertCell(bodyRow);

				if (this._GetP(this._data.ShowTabs, true))
					this._CreateHeaderContent(headerCell, data);

				if (Groups) 
				{
					for (var i=0;i<Groups.length;i++)
					{

						var group = Groups[i];
						if (typeof(group.Visible) == "undefined" || group.Visible)
							this._Group_CreateRepresentationControl(bodyCell, group,group.Index,0,this._data.ClientID);
					}
				}
				return;
			}
		}
		// FlatControl.CreateControlContent
		with (this._data)
		{
			if (Class == 'ToolBar' || Class == 'TopicBar')
			{
				if (this._data.Groups) {
					var _firstVis = true;
					for (var i=0;i<Groups.length;i++)
					{
						var group = Groups[i];
						if (typeof(group.Visible) == "undefined" || group.Visible)
						{
							if (!_firstVis && this._data.GroupSpacing)
								group.GroupSpacing = this._data.GroupSpacing;
							_firstVis = false;							 
							this._Group_CreateRepresentationControl(cell, group,group.Index,0,this._data.ClientID);
						}
					}
				}
			}	 
			else if (this._Menu || this._TreeView)
				this._CustomTree_CreateControlContent(cell);

		}
	}	

	this._Start_Item = function(c, g, gdata, data, idx)
	{
		if (!this._GetP(data.Visible, true))
			return;
		var item = c1c_init_item(data.ClientID,
								 this._GetP(data.onclick, null),
								 this._GetP(data.onselect, null),
								 this._GetP(data.onmousedown, null),
								 this._GetP(data.onmouseenter, null),
								 this._GetP(data.onmouseleave, null),
								 this._GetP(data.onmousemove, null),
								 this._GetP(data.onmouseout, null),
								 this._GetP(data.onmouseover, null),
								 this._GetP(data.onmouseup, null),
								 this._GetP(data.onmousewheel, null),
								 data.CItemStyle,
								 data.CMouseOverItemStyle,
								 data.CSelectedItemStyle,
								 data.CMouseOverSelectedItemStyle,
								 this._GetUrl(data.NavigateUrl),
								 this._GetP(data.Target, ''),
								 data.IsEnabled,
								 this._GetP(data.Selected, false),
								 this._GetP(this._data.IsClickHandler, false),
								 this._GetP(this._data.IsSelectHandler, false),
								 this._GetP(gdata.AllowSelectItem, false),
								 this._GetP(data.PostBackFunc, this._data.PostBackFunc),
								 this._GetUrl(this._GetStyleValue(data.CItemStyle, 'BackImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CItemStyle, 'ImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CItemStyle, 'LeftBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CItemStyle, 'RightBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverItemStyle, 'BackImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverItemStyle, 'ImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverItemStyle, 'LeftBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverItemStyle, 'RightBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CSelectedItemStyle, 'BackImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CSelectedItemStyle, 'ImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CSelectedItemStyle, 'LeftBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CSelectedItemStyle, 'RightBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverSelectedItemStyle, 'BackImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverSelectedItemStyle, 'ImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverSelectedItemStyle, 'LeftBorderImageUrl')),
								 this._GetUrl(this._GetStyleValue(data.CMouseOverSelectedItemStyle, 'RightBorderImageUrl')),
								 this._GetP(data.CausesValidation, false)
								);
		g.AddItem(item);
		if (data.SubMenu)
			this._Start_Group(item, data.SubMenu, 0);		 
		if (this._TreeView)
		{
			item.InitTreeItem(data.ClientID+'_ti', this._GetUrl(data.SpecialSymbolStyle.CollapsedNodeImageUrl), this._GetUrl(data.SpecialSymbolStyle.ExpandedNodeImageUrl));
			if (data.ActualPopulateOnDemand)
				item.InitTreeItemCallback(data.CallBackFunc, gdata.CallbackWaitControlID);
		}
		if (data.NestedGroup)
		{
			this._Start_Group(item, data.NestedGroup, 0); 
		}
		if (window.C1KeyboardShortcuts && this._GetP(this._data.KeyboardSupport, true) && data.KeyboardShortcut)
			window.C1KeyboardShortcuts.addShortcut(item, data.KeyboardShortcut);
	}
	this._Start_Header = function(c, gdata, header)
	{
		c.AddHeader(header.ClientID,
					this._GetP(gdata.onclick, null),
					this._GetP(gdata.onselect, null),
					this._GetP(gdata.onmousedown, null),
					this._GetP(gdata.onmouseenter, null),
					this._GetP(gdata.onmouseleave, null),
					this._GetP(gdata.onmousemove, null),
					this._GetP(gdata.onmouseout, null),
					this._GetP(gdata.onmouseover, null),
					this._GetP(gdata.onmouseup, null),
					this._GetP(gdata.onmousewheel, null),
					header.CItemStyle,
					header.CMouseOverItemStyle,
					header.CSelectedItemStyle,
					header.CMouseOverSelectedItemStyle,
					this._data.PostBackFunc,
					header.Selected,
					gdata.BodyRowClientID,
					gdata.ClientID,
					gdata.Height,
					this._GetP(this._data.GroupActivationHandler, false),
					this._GetUrl(this._GetStyleValue(header.CItemStyle, 'BackImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CItemStyle, 'ImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CItemStyle, 'LeftBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CItemStyle, 'RightBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverItemStyle, 'BackImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverItemStyle, 'ImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverItemStyle, 'LeftBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverItemStyle, 'RightBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CSelectedItemStyle, 'BackImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CSelectedItemStyle, 'ImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CSelectedItemStyle, 'LeftBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CSelectedItemStyle, 'RightBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverSelectedItemStyle, 'BackImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverSelectedItemStyle, 'ImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverSelectedItemStyle, 'LeftBorderImageUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverSelectedItemStyle, 'RightBorderImageUrl')),
					header.IsEnabled,
					this._GetP(gdata.EnableExpandCollapse, true),
					gdata.CallBackFunc, 
					gdata.CallbackWaitControlID, 
					this._GetUrl(this._GetStyleValue(header.CItemStyle, 'IndicatorUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverItemStyle, 'IndicatorUrl')),
					this._GetUrl(this._GetStyleValue(header.CSelectedItemStyle, 'IndicatorUrl')),
					this._GetUrl(this._GetStyleValue(header.CMouseOverSelectedItemStyle, 'IndicatorUrl'))
				   );
	}
	this._Start_Group = function(c, data, idx)
	{
		var act = true;
		if (typeof(data.Active) == 'boolean' && !data.Active)
			act = false;
		var ic = 0;
		if (data.Items)
			ic = data.Items.length;
		var g = c1c_init_group(data.ClientID, 
							   this._GetP(data.Enabled, true),
							   act,
							   this._GetP(data.AllowSelectItem, false),
							   this._GetP(data.AllowMultipleSelect,true),
							   this._GetP(data.AlwaysHasSelected, false),
							   this._GetP(data.AllowMultipleSelectInControl, true),
							   this._GetP(data.AllowUnselectItem, true),
							   ic,
							   '__'+data.ClientID + '_SSF');
		c.AddGroup(g);
		for(var i=0; i<ic; i++)
		{
			var item = data.Items[i];
			if (item.Class == 'LinkItem')
				this._Start_Item(c, g, data, item, i);
		}
		if(data.header)
		{
			this._Start_Header(c, data, data.header);
		}
		if (this._Menu)
			g.InitSubMenu(data.ClientID, this._GetP(data.OffsetPixelX,0), this._GetP(data.OffsetPixel0,0), this._GetP(data.Opacity,100), this._GetP(data.ShadowColor,''), this._GetP(data.ShadowDirection,135));
		else if (this._TreeView)
			g.InitTreeGroup(data.ClientID);

	}

	this._Start = function()
	{
		var el = this._rootElement;
		if (el && (this._GetP(this._data.TimeStamp, "") == "" || el.getAttribute('TimeStamp') == this._data.TimeStamp))
		{
			var _c1_control = c1c_init_control(this._data.ClientID);
			_c1_control._isMenu = this._Menu;
			_c1_control._isToolBar = this._ToolBar;
			_c1_control._isTreeView = this._TreeView;
			_c1_control._isTabStrip = this._TabStrip;
			_c1_control._isTopicBar = this._TopicBar;
			_c1_control.enableDragDrop = this._data.EnableDragDrop;
			_c1_control.causesValidation = this._data.CausesValidation;
			if (this._GetP(this._data.KeyboardSupport,true) && this._data.firstLinkItem)
			{
				_c1_control.set_keyboardSupport(true);
				if (this._data.firstLinkItem)
				{
					var ti = el.tabIndex;
					if (!ti || ti < 0)
					{
						if (document.all)
							ti = document.all.length;
						else
							ti = 1;
					}
					this._data.firstLinkItem.tabIndex = ti;
					if (ti)
						el.removeAttribute('tabIndex')
				}
			}
			if (this._Menu || this._TreeView)
				_c1_control.InitTreeControl('__'+this._data.ClientID+'_SSIF', this._GetP(this._data.AllowSelectItem, false), this._GetP(this._data.AllowUnselectItem, true), this._GetP(this._data.AllowMultipleSelect, true), this._GetP(this._data.AlwaysHasSelected, false));
			with(this._data)
					if (this._data.Groups)
			{
				for (var i=0;i<this._data.Groups.length;i++)
				{
					var group = this._data.Groups[i];
					if (typeof(group.Visible) == "undefined" || group.Visible)
						this._Start_Group(_c1_control, group,i);
				}
			}
					else if (this._data.Items)
					{
						for (var i=0;i<this._data.Items.length;i++)
						{
							var item = this._data.Items[i];
							if (this._GetP(item.Visible, true) && (item.Class == 'LinkItem'))
								this._Start_Item(_c1_control, _c1_control, this._data, item, i);
						}
					}

		}
		if (this._TopicBar)
			_c1_control.InitTopicBar(this._GetP(this._data.ViewStyle, 'Standart') == 'Button', this._GetP(this._data.AutoCollapse, false));
		if (this._TabStrip)
		{
			var leftBorderImage = this._GetUrl(this._GetStyleValue(this._data.ActiveHeaderStyle, 'LeftBorderImageUrl'));
			var mouseOverLeftBoderImage = this._GetUrl(this._GetStyleValue(this._data.MouseOverActiveHeaderStyle, 'LeftBorderImageUrl'));
			_c1_control.InitTabStrip(this._GetUrl(this._data.SeparatorInactiveImageUrl), this._GetP(this._data.MixedBordersMode, false), leftBorderImage, mouseOverLeftBoderImage);
		}
		if (this._Menu)
		{
			_c1_control.InitMenu(this._GetP(this._data.Layout, 'Vertical') == 'Vertical', this._GetP(this._data.HorzPopupDirection, 'LeftToRight') == 'LeftToRight', this._GetP(this._data.VertPopupDirection, 'TopToBottom') == 'TopToBottom', this._GetP(this._data.ClickToOpen, false), this._GetP(this._data.HideSubMenuDelay, 500));
			if (this._data.ContextMenu == 'Default')
				_c1_control.InitDefaultContextMenu();
			else if (this._data.ContextMenu == 'Control')
				_c1_control.InitControlContextMenu(this._data.ContextControlId);
			else if (this._data.ContextMenu == 'Custom')
				_c1_control.InitCustomContextMenu();
		}
		if (this._TreeView)
		{
			var psf = '__'+this._data.ClientID+'_PSF';
			var exp = this._GetP(this._data.ExpandSinglePath, false);
			if (document.getElementById(psf))
				_c1_control.InitTreeView(psf, exp);
			else
				_c1_control.InitTreeView(null, exp);
			if (this._data.GroupExpandHandler)
				_c1_control.setGroupExpandHandler();
			if (this._data.GroupCollapseHandler)
				_c1_control.setGroupCollapseHandler();
		}
		if (this._TopicBar || this._TabStrip || this._TreeView)
			_c1_control.SetGroupStatusField('__'+this._data.ClientID+'_GSF');
		if (this._data.EnableDragDrop)
			_c1_control.SetGroupOrderField('__'+this._data.ClientID+'_GOF');


		// Remove spinner
		// if (this._rootRow != this._rootElement.rows[0])
		// this._rootElement.deleteRow(0);
		// Remove content row
		if (this._contentRow && this._rootRow != this._rootElement.rows[0])
			this._rootElement.deleteRow(0);

		if (this._data.ExpandEffect)		
		{
			_c1_control.ExpandEffect = this._data.ExpandEffect;
			_c1_control.ExpandEffectDuration = this._GetP(this._data.ExpandEffectDuration, 300);
		}
		if (this._ToolBar )
			_c1_control.horizontal = this._GetP(this._data.Layout, 'Horizontal') == 'Horizontal';

		if (this._data.SortableElement)
		{	
			this._data.SortableElement.data = _c1_control;
			_c1_control.groupSpacing = data.GroupSpacing;
			Sortable.create(this._data.SortableElement, {tag: 'table', ghosting: true, onUpdate: function(list){list.data.onDragDrop(list, Sortable.sequence(list))}});
		}

	}
	this._GetP = function(value, def)
	{
		if (typeof(value) == 'undefined')
			return def;
		else
			return value;
	}
	this._GetUrl = function(idx)
	{
		if (typeof(idx)=='number' || (typeof(idx)=='string' && idx != ''))
			return this._data.Urls[idx];
		else
			return '';
	}
}

C1WebCommandBuilder.prototype.create = function(id)
{
	this._CreateControlContent();
	window.setTimeout("window."+id+".start()",10);
}
C1WebCommandBuilder.prototype.start = function()
{
	this._Start();
}
C1WebCommandBuilder.prototype.build = function(id)
{
	var el = this._rootElement;
	if (el && (this._GetP(this._data.TimeStamp, "") == "" || el.getAttribute('TimeStamp') == this._data.TimeStamp))
	{
		window.setTimeout("window."+id+".create('"+id+"')",10);
	}
}
C1WebCommandBuilder.prototype.getHash = function(vert,st,data,groupData)
{
	var cutStyle = "";
	if (st) {
		var	ss = st.split(";");
		for	(var i = 0;	i <	ss.length; i++)
		{
			if (ss[i])
			{
				var	pair = c1c_splitTwice(ss[i], ":");
				if (pair[0] != "ImageUrl")
					cutStyle += ss[i] + ';';
			}
		}
	}
	var fl = (data.NestedGroup || data.ActualPopulateOnDemand) && (data.ActualPopulateOnDemand || !this._GetP(data.NestedGroup.ActualActive, true));
	var res = ":"+data.Class+vert+cutStyle+data.NestedGroup+data.SubMenu+data.ActualActive+data.Selected+data.IsEnabled+this.specialSymbolStyleToStr(data.SpecialSymbolStyle)+data.MarkType+data.HasDropDownButton+groupData.ShowLines+groupData.ShowCheckBoxes+groupData.IconBarWidth+data.ShowLines+data.ShowCheckBox+fl+data.KeyboardShortcut;

	return res;
}
C1WebCommandBuilder.prototype.getFromHashTable = function(hash)
{
	for(var i=0; i<this._hashEls.length;i++)
	{
		if (this._hashEls[i][0] == hash)
			return this._hashEls[i];
	}
	return null;
}
C1WebCommandBuilder.prototype.addElToHash = function(hash, el, id)
{
	this._hashEls[this._hashEls.length] = [hash, el, id];
}

C1WebCommandBuilder.prototype.setNewIds = function(el, oldId, newId, data)
{
	var idLen = oldId.length;
	if (el.id && el.id.indexOf(oldId) == 0)
		el.id = newId + el.id.substr(idLen);
	if (el.id == newId)
		data.toolTipElement = el;
	else if (el.id == newId+"_txt")
		data.textElement = el;
	else if (el.id == newId+"_img")
		data.imageElement = el;
	else if (el.id == newId+"_ind")
		data.indicatorElement = el;
	else if (el.id == newId+"_lbi")
		data.lbiElement = el;
	else if (el.id == newId+"_rbi")
		data.rbiElement = el;
	else if (el.id == newId+"_ti")
		data.tiElement = el;
	else if (el.id == newId+"_cbx")
		data.cbxElement = el;
	else if (el.id == newId+"_dropBtn")
		data.dropElement = el;
	var kids = el.childNodes;
	for (var i = 0; i < kids.length; i++) 
		this.setNewIds(kids[i], oldId, newId, data);
}
C1WebCommandBuilder.prototype.setNewText = function(data)
{
	if (!data.ImageOnly)
		data.textElement.innerHTML = this._GetP(data.Text,'');
}
C1WebCommandBuilder.prototype.setNewToolTip = function(data)
{
	data.toolTipElement.title = this._GetP(data.ToolTip,'');
}
C1WebCommandBuilder.prototype.setNewImage = function(data)
{
	if (!data.TextOnly)
	{ 
		data.imageElement.onload = this._onload;
		if (data.ImageUrl)
			data.imageElement.src = this._data.Urls[data.ImageUrl];
		else
		{
			data.imageElement.src = this._data.Urls[0];
			data.imageElement.style.display = 'none';
		}
	}
}
C1WebCommandBuilder.prototype.setImageSize = function(data)
{
	if (data.indicatorElement)
		data.indicatorElement.onload = this._onload;
	if (data.lbiElement)
		data.lbiElement.onload = this._onload;
	if (data.rbiElement)
		data.rbiElement.onload = this._onload;
	if (data.tiElement)
	{
		data.tiElement.onload = this._onload;
		data.tiElement.onclick = SetPlusMinusClicked;
	}
	if (data.cbxElement)
		data.cbxElement.onclick = SetCheckboxClicked;
	if (data.dropElement)
		data.dropElement.onclick = this._dropDownButtonFunc;
}
C1WebCommandBuilder.prototype.specialSymbolStyleToStr = function(gst)
{
	var res = "sst:";
	if (gst.CheckMarkImageUrl)
		res += "1:" + gst.CheckMarkImageUrl;
	if (gst.RadioMarkImageUrl)
		res += "2:" + gst.RadioMarkImageUrl;
	if (gst.SubMenuMarkImageUrl)
		res += "3:" + gst.SubMenuMarkImageUrl;
	if (gst.SubMenuMarkText)
		res += "4:" + gst.SubMenuMarkText;
	if (gst.CollapsedNodeImageUrl)
		res += "4:" + gst.CollapsedNodeImageUrl;
	if (gst.NoExpandNodeImageUrl)
		res += "4:" + gst.NoExpandNodeImageUrl;
	if (gst.ExpandedNodeImageUrl)
		res += "4:" + gst.ExpandedNodeImageUrl;
	if (gst.VerticalLineImageUrl)
		res += "4:" + gst.VerticalLineImageUrl;
	if (gst.HorizontalLineImageUrl)
		res += "4:" + gst.HorizontalLineImageUrl;
	return res;
}
C1WebCommandBuilder.prototype._onload = function () {this.style.width='';this.style.height='';};
C1WebCommandBuilder.prototype.cloneItem = function(elToClone, id, data)
{
	var	 res = elToClone[1].cloneNode(true);
	this.setNewIds(res,elToClone[2],id,data);
	this.setNewText(data);
	this.setNewToolTip(data);
	this.setNewImage(data);
	this.setImageSize(data);
	return res;
}
C1WebCommandBuilder.prototype._dropDownButtonFunc = function () { OnDropDownClick(this, this._dropDownContextMenuId) };