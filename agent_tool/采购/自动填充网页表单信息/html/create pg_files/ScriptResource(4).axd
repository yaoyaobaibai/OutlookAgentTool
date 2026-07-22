
window.c1webi__mouse_button_state=0;window.c1webi_BrowserDetect={init:function(){this.browser=this.searchString(this.dataBrowser)||"An unknown browser";this.version=this.searchVersion(navigator.userAgent)||this.searchVersion(navigator.appVersion)||"an unknown version";this.OS=this.searchString(this.dataOS)||"an unknown OS";},searchString:function(data){for(var i=0;i<data.length;i++){var dataString=data[i].string;var dataProp=data[i].prop;this.versionSearchString=data[i].versionSearch||data[i].identity;if(dataString){if(dataString.indexOf(data[i].subString)!=-1)return data[i].identity;}else if(dataProp)return data[i].identity;}},searchVersion:function(dataString){var index=dataString.indexOf(this.versionSearchString);if(index==-1)return;return parseFloat(dataString.substring(index+this.versionSearchString.length+1));},dataBrowser:[{string:navigator.userAgent,subString:"OmniWeb",versionSearch:"OmniWeb/",identity:"OmniWeb"},{string:navigator.vendor,subString:"Apple",identity:"Safari"},{prop:window.opera,identity:"Opera"},{string:navigator.vendor,subString:"iCab",identity:"iCab"},{string:navigator.vendor,subString:"KDE",identity:"Konqueror"},{string:navigator.userAgent,subString:"Firefox",identity:"Firefox"},{string:navigator.vendor,subString:"Camino",identity:"Camino"},{string:navigator.userAgent,subString:"Netscape",identity:"Netscape"},{string:navigator.userAgent,subString:"MSIE",identity:"Explorer",versionSearch:"MSIE"},{string:navigator.userAgent,subString:"Gecko",identity:"Mozilla",versionSearch:"rv"},{string:navigator.userAgent,subString:"Mozilla",identity:"Netscape",versionSearch:"Mozilla"}],dataOS:[{string:navigator.platform,subString:"Win",identity:"Windows"},{string:navigator.platform,subString:"Mac",identity:"Mac"},{string:navigator.platform,subString:"Linux",identity:"Linux"}]};window.c1webi_BrowserDetect.init();window.c1webi_createDelegate=function(that,thatMethod){if(arguments.length>2){var _params=[];for(var n=2;n<arguments.length;++n)_params.push(arguments[n]);return function(){return thatMethod.apply(that,_params);}}
else
return function(){return thatMethod.call(that);}}
window.c1webi_createDelegateCP=function(that,thatMethod){return function(){return thatMethod.apply(that,arguments);}}
function c1webi__repeatWebCalendarInitialization(){window[this._objId].set_webCalendar(this._webCalendarObjId);}
function c1i__trimStringAll(sString)
{while(sString.substring(0,1)==' ')
{sString=sString.substring(1,sString.length);}
while(sString.substring(sString.length-1,sString.length)==' ')
{sString=sString.substring(0,sString.length-1);}
return sString;}
function c1webi__getStyleStringFromStyle(st){var s="";if(st!=null){if(st.color!=null)
s+="color:"+st.color+";";if(st.fontFamily!=null)
s+="font-family:"+st.fontFamily+";";if(st.fontStyle!=null)
s+="font-style:"+st.fontStyle+";";if(st.fontSize!=null)
s+="font-size:"+st.fontSize+";";if(st.fontVariant!=null)
s+="font-variant:"+st.fontVariant+";";if(st.fontWeight!=null)
s+="font-weight:"+st.fontWeight+";";if(st.textDecoration!=null)
s+="text-decoration:"+st.textDecoration+";";}
return s;}
function c1wsch__encode_utf8(rohtext){rohtext=rohtext.replace(/\r\n/g,"\n");var utftext="";for(var n=0;n<rohtext.length;n++)
{var c=rohtext.charCodeAt(n);if(c<128)
utftext+=String.fromCharCode(c);else if((c>127)&&(c<2048)){utftext+=String.fromCharCode((c>>6)|192);utftext+=String.fromCharCode((c&63)|128);}
else{utftext+=String.fromCharCode((c>>12)|224);utftext+=String.fromCharCode(((c>>6)&63)|128);utftext+=String.fromCharCode((c&63)|128);}}
return utftext;}
function c1wsch__decode_utf8(utftext){var plaintext="";var i=0;var c=c1=c2=0;while(i<utftext.length)
{c=utftext.charCodeAt(i);if(c<128){plaintext+=String.fromCharCode(c);i++;}
else if((c>191)&&(c<224)){c2=utftext.charCodeAt(i+1);plaintext+=String.fromCharCode(((c&31)<<6)|(c2&63));i+=2;}
else{c2=utftext.charCodeAt(i+1);c3=utftext.charCodeAt(i+2);plaintext+=String.fromCharCode(((c&15)<<12)|((c2&63)<<6)|(c3&63));i+=3;}}
return plaintext;}
window.c__escapeArr1=['\n','\r','"','@','+'];window.c__escapeArr2=["!ESC!NN!","!ESC!RR!","!ESC!01!","!ESC!02!","!ESC!03!"];window.c__escapeArr3=["(\n)","(\r)",'(")',"(@)","(\\+)"];function c__escape(s){for(var i=0;i<window.c__escapeArr1.length;i++){var myregexp=/\+/;var r=new RegExp(window.c__escapeArr3[i],"g");s=s.replace(r,window.c__escapeArr2[i]);}
return s;}
function c__unescape(s,skipUtf){if(s==null)
return s;if(skipUtf==null||skipUtf!=true)
s=c1wsch__decode_utf8(s);for(var i=0;i<window.c__escapeArr2.length;i++){var r=new RegExp("("+window.c__escapeArr2[i]+")","g");s=s.replace(r,window.c__escapeArr1[i]);}
return s;}
function c1webi__document_keydown(e){e=e||window.event;if(e==null)return;var k=e.which||e.keyCode;if(k==27){if(window.WIWS__WebCalendarListenersMan!=null){var arr=window.WIWS__WebCalendarListenersMan.calendars;for(var i=0;i<arr.length;i++){if(arr[i].IsPopupShowing())
arr[i].Close();}}}}
function c1webi__document_mouseover(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;}
function c1webi__document_mouseout(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;}
function c1webi__doInlineFFfix(aInputObj,pos,actionType,e){var btnNum=0;var targetDom=null;if(actionType==1||actionType==2||actionType==3){if(aInputObj.___upbtnpresent==true){var aTdTag=window[aInputObj._cache_id]["aTdTagU"];var bnd=C1WI_GetAbsoluteControlBounds(aTdTag);bnd.y-=4;if(c1webi__isPointInBounds(pos,bnd)){btnNum=1;targetDom=aTdTag;}}
if(aInputObj.___downbtnpresent==true){var aTdTag=window[aInputObj._cache_id]["aTdTagD"];var bnd=C1WI_GetAbsoluteControlBounds(aTdTag);bnd.y-=4;if(c1webi__isPointInBounds(pos,bnd)){btnNum=2;targetDom=aTdTag;}}
if(aInputObj.___custombtnpresent==true){var aTdTag=window[aInputObj._cache_id]["aTdTagC"];var bnd=C1WI_GetAbsoluteControlBounds(aTdTag);bnd.y-=4;if(c1webi__isPointInBounds(pos,bnd)){btnNum=3;targetDom=aTdTag;}}}
if(targetDom!=null){if(window.dasfasfAsfasfasfasfas_prev_dom!=null&&window.dasfasfAsfasfasfasfas_prevbtn!=btnNum){window.dasfasfAsfasfasfasfas_prev_dom.onmouseout(e);window.dasfasfAsfasfasfasfas_prev_dom=null;}
if(actionType==2){targetDom.onmousedown(e);}
else if(actionType==3){targetDom.onmouseup(e);}else{if(window.c1webi__mouse_button_state==1){}else{targetDom.onmouseover(e);}}
window.dasfasfAsfasfasfasfas_prev_dom=targetDom;window.dasfasfAsfasfasfasfas_prevbtn=btnNum;}else{if(window.dasfasfAsfasfasfasfas_prev_dom!=null){window.dasfasfAsfasfasfasfas_prev_dom.onmouseout(e);window.dasfasfAsfasfasfasfas_prev_dom=null;}}}
function c1webi__document_mousemove(e){e=e||window.event;if(e==null)
return;var target=e.srcElement||e.target;if(target==null)
return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;if(target._inlineContanerFix==1){var pos=c1webi__getMousePointerPosition(e);var aInputObj=window[target._objId];c1webi__doInlineFFfix(aInputObj,pos,1,e);}}
function c1webi__document_mouseup(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;window.c1webi__mouse_button_state=0;if(target._inlineContanerFix==1){var pos=c1webi__getMousePointerPosition(e);var aInputObj=window[target._objId];c1webi__doInlineFFfix(aInputObj,pos,3,e);}}
function c1webi__isPointInBounds(point,bounds){if(point.x>=bounds.x&&point.x<=(bounds.x+bounds.width)){if(point.y>=bounds.y&&point.y<=(bounds.y+bounds.height))
return true;}
return false;}
function c1webi__getMousePointerPosition(e){if(!e){e=window.event;}
var cursor={x:0,y:0};var ev=e;if(ev['pageX']||ev['pageY']){cursor.x=ev['pageX'];cursor.y=ev['pageY'];}
else{var de=document.documentElement;var b=document.body;cursor.x=ev['clientX']+(((de.scrollLeft))?de.scrollLeft:b.scrollLeft)-(((de.clientLeft))?de.clientLeft:0);cursor.y=ev['clientY']+(((de.scrollTop))?de.scrollTop:b.scrollTop)-(((de.clientTop))?de.clientTop:0);}
return cursor;}
function c1webi__document_mousedown(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;window.c1webi__mouse_button_state=1;if(target._inlineContanerFix==1){var pos=c1webi__getMousePointerPosition(e);var aInputObj=window[target._objId];c1webi__doInlineFFfix(aInputObj,pos,2,e);}
if(window.WIWS__WebCalendarListenersMan!=null){var arr=window.WIWS__WebCalendarListenersMan.calendars;for(var i=0;i<arr.length;i++){var skipHide=false;var aCal=arr[i];if(aCal.IsPopupShowing()){var aDestObjs=window.WIWS__WebCalendarListenersMan.listeners[aCal.ID];if(aDestObjs!=null){for(var j=0;j<aDestObjs.length;j++){if(target.aInputObjGlobalObjId!=null&&target.aInputObjGlobalObjId==aDestObjs[j]){skipHide=true;break;}}}
if(skipHide!=true){}}}}}
function WIWS__WebCalendarListeners(){}
WIWS__WebCalendarListeners.prototype={listen:function(aCal,aDestObjId){if(this.listeners[aCal.ID]==null)
this.listeners[aCal.ID]=new Array();this.listeners[aCal.ID].push(aDestObjId);this.calendars.push(aCal);aCal.OnSelChange=this.OnSelChangeHandler;aCal.PopupSetting.AutoCollapse=true;},OnSelChangeHandler:function(aCal,seltype,seldates){if(aCal!=null){var arr=window.WIWS__WebCalendarListenersMan.listeners[aCal.ID];if(arr!=null){for(var i=0;i<arr.length;i++){var aObjId=arr[i];if(window[aObjId]["_C1WebCalendar_SelChange"]!=null)
window[aObjId]._C1WebCalendar_SelChange(aCal,seltype,seldates);else
if(window[aObjId]["_c1WebCalendar_OnSelChange"]!=null)
window[aObjId]._c1WebCalendar_OnSelChange(aCal,seltype,seldates);}}}},calendars:[],listeners:{}}
if(window.WIWS__WebCalendarListenersMan==null){window.WIWS__WebCalendarListenersMan=new WIWS__WebCalendarListeners();}
var Generate__UniqId_countWEbInput=0;function Generate__UniqIdWebInputUsage(){try{Generate__UniqId_countWEbInput++;if(Generate__UniqId_countWEbInput==NaN)
Generate__UniqId_countWEbInput=0;return Generate__UniqId_countWEbInput;}catch(ex){Generate__UniqId_countWEbInput=0;}}
function get_element_by___id(aElementId){var pElem=window[aElementId];if(!pElem){pElem=document.getElementById(aElementId);}
return pElem;}
function Add__EventListener(evname,el,func){if(el.attachEvent){el.attachEvent("on"+evname,func);}else if(el.addEventListener){el.addEventListener(evname,func,true);}else{el["on"+evname]=func;}};function find_First_Child___by__tag_Name(aParent,aTagName){for(var i=0;i<aParent.childNodes.length;i++){if(aParent.childNodes.item(i).nodeName==aTagName){return aParent.childNodes.item(i);}}
return null;}
function GetControlLocation(element)
{var offsetX=0;var offsetY=0;var parent;for(parent=element;parent;parent=parent.offsetParent){if(parent.offsetLeft){offsetX+=parent.offsetLeft;}
if(parent.offsetTop){offsetY+=parent.offsetTop;}}
return{x:offsetX,y:offsetY};}
function GetControlBounds(element){var offset=GetControlLocation(element);var width=element.offsetWidth;var height=element.offsetHeight;return{x:offset.x,y:offset.y,width:width,height:height};}
function C1WI_GetAbsoluteControlBounds(element){var aCntrlBnds=GetControlBounds(element);var aTotalScrollTop=0;var aTotalScrollLeft=0;var aInspElem=element;while(aInspElem!=null){if(aInspElem.tagName=="HTML")
break;if(aInspElem.scrollLeft!=null)
aTotalScrollLeft+=aInspElem.scrollLeft;if(aInspElem.scrollTop!=null)
aTotalScrollTop+=aInspElem.scrollTop;aInspElem=aInspElem.parentNode;}
var aCalculatedLeft=aCntrlBnds.x-aTotalScrollLeft;var aCalculatedTop=aCntrlBnds.y-aTotalScrollTop;if(aCalculatedTop<0)
aCalculatedTop=0;if(aCalculatedLeft<0)
aCalculatedLeft=0;aCntrlBnds.y=aCalculatedTop;aCntrlBnds.x=aCalculatedLeft;return aCntrlBnds;}
function c1webinputcombo__hideComboDiv(aInputObj){if(aInputObj==null)
return;if(aInputObj.__ext_extends_combo!=null){aInputObj.__ext_extends_combo._div.style.display="none";aInputObj.__ext_extends_combo._div.parentNode.removeChild(aInputObj.__ext_extends_combo._div);if(aInputObj.__ext_extends_combo._ieFrame!=null){aInputObj.__ext_extends_combo._ieFrame.style.display="none";aInputObj.__ext_extends_combo._ieFrame.parentNode.removeChild(aInputObj.__ext_extends_combo._ieFrame);}
Remove__EventListener("mousedown",document,aInputObj.__ext_extends_combo._docMouseDownDel);Remove__EventListener("mouseup",document,aInputObj.__ext_extends_combo._docMouseUpDel);Remove__EventListener("mouseover",document,aInputObj.__ext_extends_combo._docMouseOverDel);Remove__EventListener("mouseout",document,aInputObj.__ext_extends_combo._docMouseOutDel);Remove__EventListener("mouseout",document,aInputObj.__ext_extends_combo._docKeyDownDel);aInputObj.__ext_extends_combo=null;}}
function c1webinputcombo__doc_mousedown(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;if(target.attributes!=null){if(target.attributes["c1cmb_input_globjid"]!=null){var aTargetInputObj=window[target.attributes["c1cmb_input_globjid"].value];if(aTargetInputObj!=null&&aTargetInputObj.__ext_extends_combo!=null){var aItem=aTargetInputObj.__ext_extends_combo._items[parseInt(target.attributes["c1cmb_row_index"].value)];aTargetInputObj.__ext_extends_combo._selectedItem=aItem;aTargetInputObj.set_Value(aItem.value,true);}}}
if(target._c1sch_skip_cmbohide!=null&&target._c1sch_skip_cmbohide==true)
return;if(target.aInputObjGlobalObjId!=null&&target.aInputObjGlobalObjId==this.aInputObjGlobalObjId)
return;c1webinputcombo__hideComboDiv(window[this.aInputObjGlobalObjId]);}
function c1webinputcombo__doc_mouseup(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;if(target._c1sch_skip_cmbohide!=null&&target._c1sch_skip_cmbohide==true)
return;if(target.aInputObjGlobalObjId!=null&&target.aInputObjGlobalObjId==this.aInputObjGlobalObjId)
return;c1webinputcombo__hideComboDiv(window[this.aInputObjGlobalObjId]);}
function c1webinputcombo__doc_keydown(e){e=e||window.event;if(e==null)return;var k=e.which||e.keyCode;if(k==27){c1webinputcombo__hideComboDiv(window[this.aInputObjGlobalObjId]);}}
function c1webinputcombo__doc_mouseover(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;if(target.attributes!=null){if(target.attributes["c1cmb_input_globjid"]!=null){var aTargetInputObj=window[target.attributes["c1cmb_input_globjid"].value];if(aTargetInputObj!=null&&aTargetInputObj.__ext_extends_combo!=null){if(aTargetInputObj.__ext_extends_combo.selectedItemElems==null)
aTargetInputObj.__ext_extends_combo.selectedItemElems=new Array();var arr=aTargetInputObj.__ext_extends_combo.selectedItemElems;for(var i=arr.length-1;i>=0;i--){arr[i].style.backgroundColor="";arr.splice(i,1);}
target.style.backgroundColor="#316AC5";arr.push(target);}}}}
function c1webinputcombo__doc_mouseout(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;if(target==null)return;while(target._c1_dom_isTargetToParentNode==true&&target.parentNode!=null)target=target.parentNode;if(target.attributes!=null){if(target.attributes["c1cmb_input_globjid"]!=null){var aTargetInputObj=window[target.attributes["c1cmb_input_globjid"].value];if(aTargetInputObj!=null&&aTargetInputObj.__ext_extends_combo!=null){target.style.backgroundColor="";}}}}
function c1webinputcombo__fillItemsContent(aInputObj,aItemsArr){var aInputObjGlobalObjId=aInputObj.id+"Obj";if(window[aInputObjGlobalObjId]==null){window[aInputObjGlobalObjId]=aInputObj;}
var aInputElem=aInputObj.getInputElement();var sInputElemStStr=c1webi__getStyleStringFromStyle(aInputElem.style);var aInputObjText=c1i__trimStringAll(aInputObj.get_TextWithPromptAndLiterals());var aInputObjValue=aInputObj.get_Value();aInputObj.__ext_extends_combo._selectedIndex=null;aInputObj.__ext_extends_combo._selectedIndex_itemsCount=aItemsArr.length;var aTable=document.createElement("TABLE");aTable.border=0;aTable.cellSpacing=0;aTable.cellPadding=0;aTable.width="100%";for(var i=0;i<aItemsArr.length;i++){var aRow=aTable.insertRow(i);var aCell=aRow.insertCell(0);aCell.style.cssText='white-space:nowrap;height:18px;'+sInputElemStStr;var s="";s+='<div c1cmb_row_index="'+i+'" c1cmb_input_globjid="'+aInputObjGlobalObjId+'" style="padding-top:2px;padding-bottom:2px;overflow:hidden;cursor:default;font-size:8pt;font-family:Verdana;">';s+=aItemsArr[i].text;s+="</div>";aCell.innerHTML=s;var aDiv=aCell.firstChild;var aFirstChild=aDiv.firstChild;while(aFirstChild!=null&&aFirstChild.nodeName!=null&&aFirstChild.nodeName!="#text"){try{aFirstChild["_c1_dom_isTargetToParentNode"]=true;}catch(ex){break;}
aFirstChild=aFirstChild.firstChild;}
var aCurItemSelected=false;if(aItemsArr[i].value!=null){if(typeof(aItemsArr[i].value)=="string"){if(c1i__trimStringAll(aItemsArr[i].value)==aInputObjText){aCurItemSelected=true;}}else if((typeof(aItemsArr[i].value)=="object"&&aItemsArr[i].value.getTime!=null)&&(typeof(aInputObjValue)=="object"&&aInputObjValue.getTime!=null)){if(aItemsArr[i].value.getTime()==aInputObjValue.getTime()){aCurItemSelected=true;}}else{if(aItemsArr[i].value==aInputObjValue){aCurItemSelected=true;}}}
if(aCurItemSelected==true||aItemsArr[i].text==aInputObjText){aCell.firstChild.style.backgroundColor="#316AC5";aInputObj.__ext_extends_combo._selectedItem=aItemsArr[i];if(aInputObj.__ext_extends_combo.selectedItemElems==null)
aInputObj.__ext_extends_combo.selectedItemElems=new Array();aInputObj.__ext_extends_combo.selectedItemElems.push(aCell.firstChild);aInputObj.__ext_extends_combo._selectedIndex=i;}}
aInputObj.__ext_extends_combo._div.innerHTML="";aInputObj.__ext_extends_combo._div.appendChild(aTable)}
function c1webinput__getMaxZindexForElem(aEl){var _c1schTopIndex=10;if(aEl==null||aEl.parentNode==null)
return _c1schTopIndex;var aInspCurElem=aEl.parentNode;while(aInspCurElem!=null){if(aInspCurElem.style!=null&&aInspCurElem.style.zIndex!=null){if(aInspCurElem.style.zIndex>_c1schTopIndex){_c1schTopIndex=aInspCurElem.style.zIndex*1;}}
aInspCurElem=aInspCurElem.parentNode;}
if(_c1schTopIndex<10)
_c1schTopIndex=10;return _c1schTopIndex;}
function c1webinputcombo__scrollToSelectedItem(aInputObj){if(aInputObj.__ext_extends_combo._selectedIndex!=null){var aSH=aInputObj.__ext_extends_combo._div.scrollHeight;var aCalculatedScrollTop=0;if(aSH!=null&&aSH>0){aSH=aInputObj.__ext_extends_combo._div.scrollHeight;var ddd=aSH/aInputObj.__ext_extends_combo._selectedIndex_itemsCount;aCalculatedScrollTop=aInputObj.__ext_extends_combo.selectedItemElems[0].parentNode.offsetTop;}
aInputObj.__ext_extends_combo._div.scrollTop=aCalculatedScrollTop;}
var aZind=c1webinput__getMaxZindexForElem(window[aInputObj._cache_id]["elem"])
aInputObj.__ext_extends_combo._div.style.zIndex=aZind;if(aInputObj.__ext_extends_combo._ieFrame!=null){aInputObj.__ext_extends_combo._ieFrame.style.zIndex=aZind;}}
function EnumPartsHelperWindow(aParentElem){var pThis=this;this.ownerMaskedEditObject=aParentElem;this.prevHintWindow=null;this._stopAutoIncDec=false;this._autoIncDecTimerId=-1;this.doIncDecEnumPart=function(aIsDec,aPos,aEnumObject,oTextNode){pThis._stopAutoIncDec=false;if(pThis._autoIncDecTimerId!=-1){window.clearTimeout(pThis._autoIncDecTimerId);pThis._autoIncDecTimerId=-1;}
if(aIsDec)
pThis.ownerMaskedEditObject.C1MaskedTextProvider_.doDecrementEnumerationPart(aPos);else
pThis.ownerMaskedEditObject.C1MaskedTextProvider_.doIncrementEnumerationPart(aPos);pThis._autoIncDecTimerId=window.setTimeout(function(){pThis.doIncDecEnumPart(aIsDec,aPos,aEnumObject,oTextNode);},400);oTextNode.nodeValue="..."+aEnumObject.currentDigitValue+"...";pThis.ownerMaskedEditObject.updateControlText(true);}
this.doStopIncDecEnumPart=function(){pThis._stopAutoIncDec=true;if(pThis._autoIncDecTimerId!=-1){window.clearTimeout(pThis._autoIncDecTimerId);pThis._autoIncDecTimerId=-1;}}
this.show=function(aEnumObject,aHideInterval){pThis.hide(aHideInterval);var aElement=document.createElement("div");aElement.onmousedown=function(){window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();pThis.ownerMaskedEditObject.selectText(aEnumObject.beginIndex);},5);return false;};aElement.innerHTML="";aElement.style.fontSize="14px";aElement.style.backgroundColor="lightyellow";aElement.style.borderWidth="1px";aElement.style.padding="2px";aElement.style.borderStyle="solid";aElement.style.borderColor="black";aElement.style.position="absolute";var aControlBounds=GetControlBounds(window[this.ownerMaskedEditObject._cache_id]["elem"]);aElement.style.top=(aControlBounds.y+aControlBounds.height+2)+"px";var aInputTextAlign="";if(window[this.ownerMaskedEditObject._cache_id]["elem"].style!=null)
aInputTextAlign=window[this.ownerMaskedEditObject._cache_id]["elem"].style.textAlign;aInputTextAlign=(""+aInputTextAlign+"").toLowerCase();var arr=aEnumObject.GetArrayOfAvilableValues();var aCurIndex=aEnumObject.curValueIndex;if(aEnumObject.EnumPartType_==EnumPartType.Degit){var oTextNode=document.createTextNode("");oTextNode.nodeValue="..."+aEnumObject.currentDigitValue+"...";var aLink=document.createElement("a");aLink.beginIndex=aEnumObject.beginIndex;aLink.innerHTML="<font color=black><b><<</b></font>";aLink.href="javascript:void(0)";aLink.style.textDecoration="none";aLink.onmousedown=function(){window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();},5);return false;};aLink.onmouseover=function(){pThis.doIncDecEnumPart(true,this.beginIndex,aEnumObject,oTextNode);return false;};aLink.onmouseout=function(){pThis.doStopIncDecEnumPart();return false;};aElement.appendChild(aLink);aLink=document.createElement("a");aLink.index=0;aLink.innerHTML="<font color=black>"+arr[0]+"</font>";aLink.href="javascript:void(0)";aLink.style.textDecoration="none";aLink.onmousedown=function(){pThis.ownerMaskedEditObject.C1MaskedTextProvider_.doSetEnumerationIndex(this.index,aEnumObject);pThis.ownerMaskedEditObject.updateControlText(true);window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();},5);pThis.hide(1);return false;};aElement.appendChild(aLink);aElement.appendChild(oTextNode);aLink=document.createElement("a");aLink.index=1;aLink.innerHTML="<font color=black>"+arr[1]+"</font>";aLink.href="javascript:void(0)";aLink.style.textDecoration="none";aLink.onmousedown=function(){pThis.ownerMaskedEditObject.C1MaskedTextProvider_.doSetEnumerationIndex(this.index,aEnumObject);pThis.ownerMaskedEditObject.updateControlText(true);window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();},5);pThis.hide(1);return false;};aElement.appendChild(aLink);aLink=document.createElement("a");aLink.beginIndex=aEnumObject.beginIndex;aLink.innerHTML="<font color=black><b>>></b></font>";aLink.href="javascript:void(0)";aLink.style.textDecoration="none";aLink.onmousedown=function(){window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();},5);return false;};aLink.onmouseover=function(){pThis.doIncDecEnumPart(false,this.beginIndex,aEnumObject,oTextNode);return false;};aLink.onmouseout=function(){pThis.doStopIncDecEnumPart();return false;};aElement.appendChild(aLink);}else{for(var i=0;i<arr.length;i++){var aLink=document.createElement("a");aLink.index=i;if(aEnumObject.EnumPartType_==EnumPartType.Degit){aLink.innerHTML="<font color=black>"+arr[i]+"</font>";}else{if(i==aCurIndex){aLink.innerHTML="<font color=black><b>"+arr[i]+"</b></font>";}else{aLink.innerHTML="<font color=black>"+arr[i]+"</font>";}}
aLink.href="javascript:void(0)";aLink.style.textDecoration="none";aLink.onmousedown=function(){pThis.ownerMaskedEditObject.C1MaskedTextProvider_.doSetEnumerationIndex(this.index,aEnumObject);pThis.ownerMaskedEditObject.updateControlText(true);window.setTimeout(function(){window[pThis.ownerMaskedEditObject._cache_id]["elem"].focus();},5);pThis.hide(1);return false;};aElement.appendChild(aLink);if(aEnumObject.EnumPartType_==EnumPartType.Degit&&i==0){var oTextNode=document.createTextNode("...");aElement.appendChild(oTextNode);}else{var oTextNode=document.createTextNode(" ");aElement.appendChild(oTextNode);}}}
this.prevHintWindow=aElement;document.body.appendChild(aElement);aElement.style.zIndex=c1webinput__getMaxZindexForElem(window[this.ownerMaskedEditObject._cache_id]["elem"]);var aHintElemControlBounds=GetControlBounds(aElement);switch(aInputTextAlign){case"center":aElement.style.left=(aControlBounds.x+(aControlBounds.width-aHintElemControlBounds.width)/2)+"px";break;case"right":aElement.style.left=(aControlBounds.x+aControlBounds.width-aHintElemControlBounds.width-aControlBounds.width/50)+"px";break;default:aElement.style.left=(aControlBounds.x+aControlBounds.width/50)+"px";break;}}
this.hide=function(aHideInterval){if(aHideInterval==undefined)
aHideInterval=200;var aPrevWindow=pThis.prevHintWindow;pThis.prevHintWindow=null;window.setTimeout(function(){if(aPrevWindow!=null){pThis.doStopIncDecEnumPart();document.body.removeChild(aPrevWindow);aPrevWindow=null;}},aHideInterval);}}
function create__Delegate_CP(that,thatMethod){return function(){return thatMethod.apply(that,arguments);}}
function Add__EventListener(evname,el,func){if(el.attachEvent){el.attachEvent("on"+evname,func);}else if(el.addEventListener){el.addEventListener(evname,func,true);}else{el["on"+evname]=func;}};function Remove__EventListener(evname,el,func){if(el.detachEvent){el.detachEvent("on"+evname,func);}else if(el.removeEventListener){el.removeEventListener(evname,func,true);}else{el["on"+evname]=null;}};function C1MaskedEdit(idOrElem,Mask){if(Mask!=null)
Mask=c__unescape(Mask,true);var pThis=this;var id="";if((idOrElem instanceof String)||idOrElem.tagName==undefined||idOrElem.tagName.toLowerCase()!="input"){id=idOrElem;pThis.elem=get_element_by___id(id);}else{pThis.elem=idOrElem;if(idOrElem.id==undefined||idOrElem.id==""){idOrElem.id="temp_id_"+new Date().getTime()+Math.floor(Math.random()*(100000-1+1)+1);}
id=idOrElem.id;}
pThis.id=id;if(pThis.elem==null){window.status="C1WebInput initialization error";}
pThis._cache_id=pThis.id+"_HtmlElemsCache";window[pThis._cache_id]=new Object();window[pThis._cache_id]["elem"]=pThis.elem;window[pThis._cache_id]["elemTbl"]=get_element_by___id(id+"TBL");if(window[pThis._cache_id]["elemTbl"]==null){window[pThis._cache_id]["elemTbl"]=window[pThis._cache_id]["elem"];}else{try{if(c1webi_BrowserDetect.browser!="Explorer"){if(window[pThis._cache_id]["elemTbl"].parentNode.parentNode.parentNode.parentNode.style.display=="inline"){var aInlineContainer=window[pThis._cache_id]["elemTbl"].parentNode.parentNode.parentNode.parentNode;try{aInlineContainer._inlineContanerFix=1;aInlineContainer._id=pThis.id;aInlineContainer._objId=pThis.id+"Obj";aInlineContainer._cache_id=pThis._cache_id;}catch(ex){}
var aTdTagU=get_element_by___id(pThis.id+"_sbu_td");if(aTdTagU!=null){pThis.___upbtnpresent=true;window[pThis._cache_id]["aTdTagU"]=aTdTagU;}
var aTdTagD=get_element_by___id(pThis.id+"_sbd_td");if(aTdTagD!=null){pThis.___downbtnpresent=true;window[pThis._cache_id]["aTdTagD"]=aTdTagD;}
var aTdTagC=get_element_by___id(pThis.id+"_cb_td");if(aTdTagC!=null){pThis.___custombtnpresent=true;window[pThis._cache_id]["aTdTagC"]=aTdTagC;}}}}catch(ex){}}
pThis.elem=null;idOrElem=null;var aElemViewState=get_element_by___id(id+"_ViewState");if(aElemViewState!=null){aElemViewState.value="-";}else{aElemViewState=new Object();aElemViewState.value="";}
window[pThis._cache_id]["ViewStateElem"]=aElemViewState;aElemViewState=null;pThis.C1MaskedTextProvider_=new C1MaskedTextProvider();pThis.C1MaskedTextProvider_._parentMaskEdit=pThis;pThis.isMaskNull=false;try{pThis.C1MaskedTextProvider_.constructor(Mask,false);}catch(e){pThis.isMaskNull=true;}
pThis.EnumPartsHelperWindow_=new EnumPartsHelperWindow(this);pThis.InvalidInputColor=null;pThis.isControlFocused=false;pThis.isInvalidInputColorShowing=false;pThis.isControlInitialized=false;this.toBool=function(value){value=""+value+"";if(value=="1"||value.toLowerCase()=="true"||value.toLowerCase()=="yes")
return true;return false;}
this.HidePromptOnLeaveValue=false;this.HideEnterValue=false;this.ShowHintForEnumPartsValue=true;this.CustomMaskHandler=null;this.UseSystemPasswordCharValue=false;this._isInputFilterDisabled=false;this._isUserInputDisabled=false;this.OnClientBlur=null;this.OnClientFocus=null;this.OnClientInit=null;this.OnClientInvalidInput=null;this.OnClientTextChanged=null;this.OnClientDateChanged=null;this.OnClientKeyDown=null;this.OnClientKeyPress=null;this.OnClientKeyUp=null;this.OnClientMouseDown=null;this.OnClientMouseUp=null;this.OnClientMouseOver=null;this.OnClientMouseOut=null;this.OnClientCustomButtonClick=null;this.OnClientValueBoundsExceeded=null;this.setComboItems=function(arr){this._comboItemsArr=arr;}
this.clearComboItems=function(){this._comboItemsArr=null;}
this.setComboListWidth=function(aWidth){this._comboListWidth=aWidth;}
this.setMaxComboListHeight=function(aHeight){this._comboListHeight=aHeight;}
this._popupComboList=function(){if(!pThis.isAllowEditControlValueByUser()){return;}
if(this.__ext_extends_combo!=null){c1webinputcombo__hideComboDiv(this);return;}
if(this._comboItemsArr==null)
return
if(this._comboItemsArr.length==0)
return;var aItemsArr=this._comboItemsArr;var aInputObjGlobalObjId=pThis._objId;var aCntrlBnds=C1WI_GetAbsoluteControlBounds(window[pThis._cache_id]["elemTbl"]);if(c1webi_BrowserDetect.browser!="Explorer"){try{var aCntrlBnds222=C1WI_GetAbsoluteControlBounds(window[pThis._cache_id]["elem"]);var dif=aCntrlBnds222.y-aCntrlBnds.y;aCntrlBnds.height=aCntrlBnds.height+dif*2;aCntrlBnds.y=aCntrlBnds222.y;}catch(exx3){try{if(window[pThis._cache_id]["elemTbl"].attributes!=null){if(window[pThis._cache_id]["elemTbl"].attributes["c1_bounds"]!=null){var sBoundsStr=window[pThis._cache_id]["elemTbl"].attributes["c1_bounds"].value;var aBndsArr=sBoundsStr.split("|");var aYHeight=aBndsArr[1].replace("px","")*1;aCntrlBnds.y=aYHeight;}}}catch(exx0){}}}
var aInputObj=pThis;if(aInputObj.__ext_extends_combo==null){aInputObj.__ext_extends_combo=new Object();var aInputElem=aInputObj.getInputElement();var aSelDiv;if(c1webi_BrowserDetect.browser=="Explorer"){aSelDiv=document.createElement("IFRAME");aSelDiv._c1sch_skip_cmbohide=true;aSelDiv.style.display="none";aSelDiv.style.position="absolute";aSelDiv.style.backgroundColor="white";aSelDiv.style.zIndex=999;document.body.appendChild(aSelDiv);aInputObj.__ext_extends_combo._ieFrame=aSelDiv;}
aSelDiv=document.createElement("DIV");aSelDiv._c1sch_skip_cmbohide=true;aSelDiv.style.display="none";aSelDiv.style.position="absolute";aSelDiv.style.backgroundColor="white";aSelDiv.style.borderStyle="solid";aSelDiv.style.borderColor="black";aSelDiv.style.borderWidth="1px";aSelDiv.style.overflow="auto";aSelDiv.style.overflowX="hidden";aSelDiv.style.overflowY="hidden";aSelDiv.style.zIndex=1000;aSelDiv.innerHTML="asdasD";aInputObj.__ext_extends_combo._div=aSelDiv;c1webinputcombo__fillItemsContent(aInputObj,aItemsArr);document.body.appendChild(aSelDiv);var aProxyObj={aInputObjGlobalObjId:aInputObjGlobalObjId};aInputObj.__ext_extends_combo._docMouseDownDel=c1webi_createDelegateCP(aProxyObj,c1webinputcombo__doc_mousedown);aInputObj.__ext_extends_combo._docMouseUpDel=c1webi_createDelegateCP(aProxyObj,c1webinputcombo__doc_mouseup);aInputObj.__ext_extends_combo._docMouseOverDel=c1webi_createDelegateCP(aProxyObj,c1webinputcombo__doc_mouseover);aInputObj.__ext_extends_combo._docMouseOutDel=c1webi_createDelegateCP(aProxyObj,c1webinputcombo__doc_mouseout);aInputObj.__ext_extends_combo._docKeyDownDel=c1webi_createDelegateCP(aProxyObj,c1webinputcombo__doc_keydown);}
var aCalculatedWidth=(aCntrlBnds.width-2);var aCalculatedTop=aCntrlBnds.y+aCntrlBnds.height;if(aInputObj._comboListWidth!=null&&aInputObj._comboListWidth>=0){aCalculatedWidth=aInputObj._comboListWidth;}
aInputObj.__ext_extends_combo._items=aItemsArr;if(aInputObj.__ext_extends_combo._div!=null){var aDisplayStyle="none";if(aInputObj.__ext_extends_combo._div.style.display=="none"){aDisplayStyle="block";Add__EventListener("mousedown",document,aInputObj.__ext_extends_combo._docMouseDownDel);Add__EventListener("mouseup",document,aInputObj.__ext_extends_combo._docMouseUpDel);Add__EventListener("mouseover",document,aInputObj.__ext_extends_combo._docMouseOverDel);Add__EventListener("mouseout",document,aInputObj.__ext_extends_combo._docMouseOutDel);Add__EventListener("keydown",document,aInputObj.__ext_extends_combo._docKeyDownDel);}else{return;Remove__EventListener("mousedown",document,aInputObj.__ext_extends_combo._docMouseDownDel);Remove__EventListener("mouseup",document,aInputObj.__ext_extends_combo._docMouseUpDel);Remove__EventListener("mouseover",document,aInputObj.__ext_extends_combo._docMouseOverDel);Remove__EventListener("mouseout",document,aInputObj.__ext_extends_combo._docMouseOutDel);Remove__EventListener("keydown",document,aInputObj.__ext_extends_combo._docKeyDownDel);}
if(aInputObj.__ext_extends_combo._ieFrame!=null){aInputObj.__ext_extends_combo._ieFrame.style.top=aCalculatedTop+"px";aInputObj.__ext_extends_combo._ieFrame.style.left=aCntrlBnds.x+"px";aInputObj.__ext_extends_combo._ieFrame.style.width=aCalculatedWidth+2+"px";aInputObj.__ext_extends_combo._ieFrame.style.display=aDisplayStyle;}
if(c1webi_BrowserDetect.browser=="Explorer"){aInputObj.__ext_extends_combo._div.style.top=aCalculatedTop+"px";aInputObj.__ext_extends_combo._div.style.left=aCntrlBnds.x+"px";}else{aInputObj.__ext_extends_combo._div.style.top=aCalculatedTop-7+"px";aInputObj.__ext_extends_combo._div.style.left=aCntrlBnds.x+"px";}
aInputObj.__ext_extends_combo._div.style.width=aCalculatedWidth+"px";aInputObj.__ext_extends_combo._div.style.display=aDisplayStyle;var aCalculatedHeight=aInputObj.__ext_extends_combo._div.offsetHeight;var maxComboListHeight=250;if(aInputObj._comboListHeight!=null&&aInputObj._comboListHeight>=0){maxComboListHeight=aInputObj._comboListHeight;}
if(aCalculatedHeight>maxComboListHeight){aCalculatedHeight=maxComboListHeight;aInputObj.__ext_extends_combo._div.style.overflowY="scroll";}
if(aInputObj.__ext_extends_combo._ieFrame!=null)
aInputObj.__ext_extends_combo._ieFrame.style.height=aCalculatedHeight+2+"px";if(aInputObj.__ext_extends_combo._div!=null)
aInputObj.__ext_extends_combo._div.style.height=aCalculatedHeight+"px";if(aDisplayStyle!="none"){c1webinputcombo__scrollToSelectedItem(aInputObj);}}}
this.setDisableInputFilter=function(value){pThis._isInputFilterDisabled=value;}
this.setDisableUserInput=function(value){pThis._isUserInputDisabled=value;}
this.validateInput=function(value){pThis.doonchange();pThis._raiseTextChangedIfNeeded();pThis._raiseDateChangedIfNeeded();}
this.set_OnClientBlur=function(value){pThis.OnClientBlur=value;}
this.get_OnClientBlur=function(){return pThis.OnClientBlur;}
this.set_OnClientFocus=function(value){pThis.OnClientFocus=value;}
this.get_OnClientFocus=function(){return pThis.OnClientFocus;}
this.__is___OnClientInit_Called=false;this.set_OnClientInit=function(value){pThis.OnClientInit=value;if(pThis.__is___OnClientInit_Called==false&&pThis.isControlInitialized==true){pThis.__is___OnClientInit_Called=true;pThis.doClientEvent("OnClientInit");}}
this.get_OnClientInit=function(){return pThis.OnClientInit;}
this.set_OnClientInvalidInput=function(value){pThis.OnClientInvalidInput=value;}
this.get_OnClientInvalidInput=function(){return pThis.OnClientInvalidInput;}
this.set_OnClientTextChanged=function(value){pThis.OnClientTextChanged=value;}
this.get_OnClientTextChanged=function(){return pThis.OnClientTextChanged;}
this.set_OnClientDateChanged=this.set_onClientDateChanged=function(value){pThis.OnClientDateChanged=value;}
this.get_OnClientDateChanged=this.get_onClientDateChanged=function(){return pThis.OnClientDateChanged;}
this.set_OnClientKeyDown=function(value){pThis.OnClientKeyDown=value;}
this.get_OnClientKeyDown=function(){return pThis.OnClientKeyDown;}
this.set_OnClientKeyPress=function(value){pThis.OnClientKeyPress=value;}
this.get_OnClientKeyPress=function(){return pThis.OnClientKeyPress;}
this.set_OnClientKeyUp=function(value){pThis.OnClientKeyUp=value;}
this.get_OnClientKeyUp=function(){return pThis.OnClientKeyUp;}
this.set_OnClientMouseDown=function(value){pThis.OnClientMouseDown=value;}
this.get_OnClientMouseDown=function(){return pThis.OnClientMouseDown;}
this.set_OnClientMouseUp=function(value){pThis.OnClientMouseUp=value;}
this.get_OnClientMouseUp=function(){return pThis.OnClientMouseUp;}
this.set_OnClientMouseOver=function(value){pThis.OnClientMouseOver=value;}
this.get_OnClientMouseOver=function(){return pThis.OnClientMouseOver;}
this.set_OnClientMouseOut=function(value){pThis.OnClientMouseOut=value;}
this.get_OnClientMouseOut=function(){return pThis.OnClientMouseOut;}
this.set_OnClientCustomButtonClick=function(value){pThis.OnClientCustomButtonClick=value;}
this.get_OnClientCustomButtonClick=function(){return pThis.OnClientCustomButtonClick;}
this.set_OnClientValueBoundsExceeded=this.set_onClientValueBoundsExceeded=function(value){pThis.OnClientValueBoundsExceeded=value;}
this.get_OnClientValueBoundsExceeded=this.get_onClientValueBoundsExceeded=function(){return pThis.OnClientValueBoundsExceeded;}
pThis.doClientEvent=function(value,aArrayOfAdditionalParams){if(aArrayOfAdditionalParams==undefined)
aArrayOfAdditionalParams=new Array();if(value.indexOf("On")!=0){value=+"On"+value;}
if(pThis[value]instanceof Function){pThis[value](pThis,aArrayOfAdditionalParams.length>0?aArrayOfAdditionalParams[0]:null,aArrayOfAdditionalParams.length>1?aArrayOfAdditionalParams[1]:null);return true;}
if(pThis[value]==undefined||pThis[value]==null||pThis[value]==""){return false;}
try{window.c1_temp_ref__=pThis;window.c1_temp_refArr__=aArrayOfAdditionalParams;var s=pThis[value]+'(window.c1_temp_ref__';for(var i=0;i<aArrayOfAdditionalParams.length;i++){s+=', window.c1_temp_refArr__['+i+']';}
s+=');';eval(s);return true;}catch(e){return false;}}
this.set_WebCalendar=this.set_webCalendar=function(aWebCalId){pThis._webCalendarObjId=aWebCalId;var aCal=window[pThis._webCalendarObjId];if(aCal!=null){window.WIWS__WebCalendarListenersMan.listen(aCal,pThis._objId);var d=pThis.get_Date();aCal.UnSelectAll();aCal.SelectDate(d);aCal.DisplayDate=d;del=null;}else{if(pThis.__repeatWebCalInitCount==null)
pThis.__repeatWebCalInitCount=0;pThis.__repeatWebCalInitCount++;if(pThis.__repeatWebCalInitCount>10)
return;var prxy={_objId:pThis._objId,_webCalendarObjId:pThis._webCalendarObjId};var del=window.c1webi_createDelegateCP(prxy,c1webi__repeatWebCalendarInitialization);window.setTimeout(del,100);del=null;}}
this.set_WebCalendarPosition=this.set_webCalendarPosition=function(aWebCalPos){pThis._webCalendarPosition=aWebCalPos;}
this.get_ToolTip=function(){return window[pThis._cache_id]["elem"].title;}
this.set_ToolTip=function(value){window[pThis._cache_id]["elem"].title=value;pThis.putPostDataValue("ToolTip",value,(value==null||value==""));}
this.get_BackColor=function(){return window[pThis._cache_id]["elem"].style.backgroundColor;}
this.set_BackColor=function(value){try{window[pThis._cache_id]["elem"].style.backgroundColor=value;window[pThis._cache_id]["elemTbl"].style.backgroundColor=value;pThis.putPostDataValue("BackColor",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_BorderColor=function(){return window[pThis._cache_id]["elemTbl"].style.borderColor;}
this.set_BorderColor=function(value){try{window[pThis._cache_id]["elemTbl"].style.borderColor=value;pThis.putPostDataValue("BorderColor",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_BorderStyle=function(){return window[pThis._cache_id]["elemTbl"].style.borderStyle;}
this.set_BorderStyle=function(value){try{window[pThis._cache_id]["elemTbl"].style.borderStyle=value;pThis.putPostDataValue("BorderStyle",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_BorderWidth=function(){var aResult=window[pThis._cache_id]["elemTbl"].style.borderWidth;aResult=aResult.replace(/[p]/,"");aResult=aResult.replace(/[x]/,"");return aResult;}
this.set_BorderWidth=function(value){try{value=""+value+"";value=value.replace(/[p]/,"");value=value.replace(/[x]/,"");window[pThis._cache_id]["elemTbl"].style.borderWidth=value+"px";pThis.putPostDataValue("BorderWidth",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_CellSpacing=function(){return window[pThis._cache_id]["elemTbl"].cellSpacing;}
this.set_CellSpacing=function(value){try{window[pThis._cache_id]["elemTbl"].cellSpacing=value;pThis.putPostDataValue("CellSpacing",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_CssClass=function(){return window[pThis._cache_id]["elemTbl"].className;}
this.set_CssClass=function(value){try{window[pThis._cache_id]["elemTbl"].className=value;window[pThis._cache_id]["elem"].className=value;pThis.putPostDataValue("CssClass",value,false);}catch(ex){return false;}
return true;}
this.get_ForeColor=function(){return window[pThis._cache_id]["elem"].style.color;}
this.set_ForeColor=function(value){try{window[pThis._cache_id]["elem"].style.color=value;pThis.putPostDataValue("ForeColor",value,(value==null||value==""));}catch(ex){return false;}
return true;}
this.get_TextAlign=function(){return window[pThis._cache_id]["elem"].style.textAlign;}
this.set_TextAlign=function(value){try{pThis.putPostDataValue("TextAlign",value,(value==null||value==""));window[pThis._cache_id]["elem"].style.textAlign=value;return true;}catch(ex){return false;}}
this.set_AllowPromptAsInput=function(value){pThis.C1MaskedTextProvider_.AllowPromptAsInput=pThis.toBool(value);pThis.putPostDataValue("AllowPromptAsInput",value,(value==null||value==""));}
this.get_AllowPromptAsInput=function(){return pThis.C1MaskedTextProvider_.AllowPromptAsInput;}
this.set_Culture=function(aCulture){pThis.C1MaskedTextProvider_.set_CultureInfo(aCulture);pThis.updateControlText(false);}
this.get_Culture=function(){return pThis.C1MaskedTextProvider_.get_CultureInfo();}
this.set_CustomMaskedTextProvider=function(aCustomMaskedTextProvider){pThis.C1MaskedTextProvider_=aCustomMaskedTextProvider;pThis.C1MaskedTextProvider_._parentMaskEdit=pThis;pThis.C1MaskedTextProvider_.Initialize();pThis.updateControlText(false);}
this.get_CustomMaskedTextProvider=function(){return pThis.C1MaskedTextProvider_;}
this.set_HideEnter=function(value){pThis.HideEnterValue=pThis.toBool(value);pThis.putPostDataValue("HideEnter",value,(value==null||value==""));}
this.get_HideEnter=function(){return pThis.HideEnterValue;}
this.set_HidePromptOnLeave=function(value){if(pThis.HidePromptOnLeaveValue!=value){pThis.HidePromptOnLeaveValue=pThis.toBool(value);pThis.updateControlText(false);pThis.putPostDataValue("HidePromptOnLeave",value,(value==null||value==""));}}
this.get_HidePromptOnLeave=function(){return pThis.HidePromptOnLeaveValue;}
this.set_InvalidInputColor=function(value){pThis.InvalidInputColor=value;pThis.putPostDataValue("InvalidInputColor",value,(value==null||value==""));}
this.get_InvalidInputColor=function(){return pThis.InvalidInputColor;}
this.set_IsPassword=function(value){pThis.C1MaskedTextProvider_.IsPassword=pThis.toBool(value);pThis.updateControlText(false);pThis.putPostDataValue("IsPassword",value,(value==null||value==""));}
this.get_IsPassword=function(){return pThis.C1MaskedTextProvider_.IsPassword;}
this.set_mask=this.set_Mask=function(value){value=c__unescape(value,true);if(value==undefined||value.length<=0)
{pThis.isMaskNull=true;return;}else{pThis.isMaskNull=false;}
if(!pThis.IsInitialized())
return;var aText=pThis.get_Text();pThis.C1MaskedTextProvider_.mask=value;pThis.C1MaskedTextProvider_.initialMask=value;pThis.C1MaskedTextProvider_.Initialize();pThis.C1MaskedTextProvider_.Set(aText);pThis.updateControlText(false);pThis.putPostDataValue("Mask",value,(value==null||value==""));}
this.get_Mask=function(value){return pThis.C1MaskedTextProvider_.initialMask;}
this.set_PasswordChar=function(value){if((value+"").length>0){pThis.set_IsPassword(true);}else{pThis.set_IsPassword(false);}
value=value+" ";pThis.C1MaskedTextProvider_.PasswordChar=value.charAt(0);pThis.updateControlText(false);pThis.putPostDataValue("PasswordChar",value,(value==null||value==""));}
this.get_PasswordChar=function(){if(!pThis.IsInitialized()){return"_";}
return pThis.C1MaskedTextProvider_.PasswordChar;}
this.set_UseSystemPasswordChar=function(value){pThis.UseSystemPasswordCharValue=value;}
this.get_UseSystemPasswordChar=function(){return pThis.UseSystemPasswordCharValue;}
this.set_PromptChar=function(value){value=value+" ";if(!pThis.IsInitialized()){return false;}
pThis.C1MaskedTextProvider_.set_PromptChar(value.charAt(0));pThis.updateControlText(false);pThis.putPostDataValue("PromptChar",value,(value==null||value==""));}
this.get_PromptChar=function(){return pThis.C1MaskedTextProvider_.PromptChar;}
this.set_ResetOnPrompt=function(value){pThis.C1MaskedTextProvider_.ResetOnPrompt=pThis.toBool(value);pThis.updateControlText(false);pThis.putPostDataValue("ResetOnPrompt",value,(value==null||value==""));}
this.get_ResetOnPrompt=function(){return pThis.C1MaskedTextProvider_.ResetOnPrompt;}
this.set_ResetOnSpace=function(value){pThis.C1MaskedTextProvider_.ResetOnSpace=pThis.toBool(value);pThis.putPostDataValue("ResetOnSpace",value,(value==null||value==""));}
this.get_ResetOnSpace=function(){return pThis.C1MaskedTextProvider_.ResetOnSpace;}
this.set_ShowHintForEnumParts=function(value){pThis.ShowHintForEnumPartsValue=pThis.toBool(value);pThis.putPostDataValue("ShowHintForEnumParts",value,(value==null||value==""));}
this.get_ShowHintForEnumParts=function(){return pThis.ShowHintForEnumPartsValue;}
this.set_SkipLiterals=function(value){pThis.C1MaskedTextProvider_.SkipLiterals=pThis.toBool(value);pThis.putPostDataValue("SkipLiterals",value,(value==null||value==""));}
this.get_SkipLiterals=function(){return pThis.C1MaskedTextProvider_.SkipLiterals;}
this.set_Text=function(value){value=c__unescape(value,true);if(!pThis.IsInitialized()){window[pThis._cache_id]["elem"].value=value;pThis.updatePostData();return;}
pThis.C1MaskedTextProvider_.Set(value);pThis.updateControlText(false);}
this.get_Text=function(){if(!pThis.IsInitialized())
return window[pThis._cache_id]["elem"].value;return pThis.C1MaskedTextProvider_.ToString(true,false,false);}
this.get_TextWithPrompts=function(){if(!pThis.IsInitialized())
return window[pThis._cache_id]["elem"].value;return pThis.C1MaskedTextProvider_.ToString(true,true,false);}
this.get_TextWithLiterals=function(){if(!pThis.IsInitialized())
return window[pThis._cache_id]["elem"].value;return pThis.C1MaskedTextProvider_.ToString(true,false,true);}
this.get_TextWithPromptAndLiterals=function(){if(!pThis.IsInitialized())
return window[pThis._cache_id]["elem"].value;return pThis.C1MaskedTextProvider_.ToString(true,true,true);}
this.set_smartInputMode=this.set_SmartInputMode=function(bVal){try{pThis._smartInputMode=bVal;pThis.putPostDataValue("SmartInputMode",bVal);}catch(ex){}}
this.get_smartInputMode=this.get_SmartInputMode=function(){try{return pThis._smartInputMode;}catch(ex){return false;}}
this.set_startYear=this.set_StartYear=function(aVal){try{pThis._startYear=aVal;pThis.putPostDataValue("StartYear",aVal);}catch(ex){}}
this.get_startYear=this.get_StartYear=function(){return pThis._startYear;}
this.set_increment=this.set_Increment=function(aVal){try{pThis._increment=aVal;pThis.putPostDataValue("Increment",aVal);}catch(ex){}}
this.get_increment=this.get_Increment=function(){return pThis._increment;}
this.set_nullText=this.set_NullText=function(aVal){try{aVal=c__unescape(aVal,true);pThis._nullText=aVal;pThis.putPostDataValue("NullText",aVal,true,true);pThis.updateControlText(false);}catch(ex){}}
this.get_nullText=this.get_NullText=function(){return pThis._nullText;}
this.set_showNullText=this.set_ShowNullText=function(aVal){try{if(aVal==true){pThis.HidePromptOnLeaveValue=true;}
pThis._showNullText=aVal;pThis.putPostDataValue("ShowNullText",aVal);pThis.updateControlText(false);}catch(ex){}}
this.get_showNullText=this.get_ShowNullText=function(){return pThis._showNullText;}
this.isDateNull=this.isDateNull=function(){try{return pThis.C1MaskedTextProvider_.isDateNull();}catch(ex){}}
this.isValueNull=function(){try{return pThis.C1MaskedTextProvider_.isValueNull();}catch(ex){}}
this.get_Value=this.get_value=function(){if(pThis.C1MaskedTextProvider_.get_Value!=null){return pThis.C1MaskedTextProvider_.get_Value();}else{return pThis.get_Text();}}
this.set_Value=this.set_value=function(aValue,aExactMatch){try{if(pThis.C1MaskedTextProvider_.set_Value!=null){pThis.C1MaskedTextProvider_.set_Value(aValue);pThis.updateControlText(false);}else{var prevVal="";if(aExactMatch==true){prevVal=pThis.get_Text();}
pThis.set_Text(aValue);if(aExactMatch==true){var sVal=c1i__trimStringAll(aValue);var sText=c1i__trimStringAll(pThis.get_Text());if(sText!=sVal){sText=c1i__trimStringAll(pThis.get_TextWithPrompts());if(sText!=sVal){sText=c1i__trimStringAll(pThis.get_TextWithPromptAndLiterals());if(sText!=sVal){pThis.set_Text(prevVal);}}}}}
return true;}catch(ex){return false;}}
this.get_MinValue=function(){try{return pThis.C1MaskedTextProvider_.get_MinValue();}catch(ex){return null;}}
this.set_MinValue=function(aValue){try{pThis.C1MaskedTextProvider_.set_MinValue(aValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.get_MaxValue=function(){try{return pThis.C1MaskedTextProvider_.get_MaxValue();}catch(ex){return null;}}
this.set_MaxValue=function(aValue){try{pThis.C1MaskedTextProvider_.set_MaxValue(aValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.get_ThousandsSeparator=function(){try{return pThis.C1MaskedTextProvider_.get_ThousandsSeparator();}catch(ex){return null;}}
this.set_ThousandsSeparator=function(aBoolValue){try{pThis.C1MaskedTextProvider_.set_ThousandsSeparator(aBoolValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.get_DecimalPlaces=function(){try{return pThis.C1MaskedTextProvider_.get_DecimalPlaces();}catch(ex){return null;}}
this.set_DecimalPlaces=function(aValue){try{pThis.C1MaskedTextProvider_.set_DecimalPlaces(aValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.get_date=this.get_Date=function(){try{return pThis.C1MaskedTextProvider_.get_Date();}catch(ex){return null;}}
this.set_date=this.set_Date=function(aValue){try{pThis.C1MaskedTextProvider_.set_Date(aValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.get_DateFormat=function(){try{return pThis.C1MaskedTextProvider_.get_DateFormat();}catch(ex){return null;}}
this.set_DateFormat=function(aValue){try{pThis.C1MaskedTextProvider_.set_DateFormat(aValue);pThis.updateControlText(false);return true;}catch(ex){return false;}}
this.eventsAlreadyAdded=false;this._controlBoundsRepaired=false;this.IsInitialized=function(){if(pThis._objId==null)
pThis._objId=pThis.id+"Obj"
if(window[pThis._objId]==null){window[pThis._objId]=pThis;}
if(pThis._controlBoundsRepaired!=true){pThis._controlBoundsRepaired=true;}
if(pThis.eventsAlreadyAdded==false){pThis.eventsAlreadyAdded=true;Add__EventListener("keydown",document,c1webi__document_keydown);Add__EventListener("mousedown",document,c1webi__document_mousedown);Add__EventListener("mouseover",document,c1webi__document_mouseover);Add__EventListener("mouseout",document,c1webi__document_mouseout);Add__EventListener("mousemove",document,c1webi__document_mousemove);Add__EventListener("mouseup",document,c1webi__document_mouseup);Add__EventListener("keypress",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.dokeypress(e);}));Add__EventListener("keydown",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.dokeydown(e);}));Add__EventListener("keyup",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.dokeyup(e);}));Add__EventListener("focus",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.dofocus(e);}));Add__EventListener("blur",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doblur(e);}));Add__EventListener("mouseup",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doonmouseup(e);}));Add__EventListener("mousedown",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doonmousedown(e);}));Add__EventListener("mouseover",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doonmouseover(e);}));Add__EventListener("mouseout",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doonmouseout(e);}));Add__EventListener("change",window[pThis._cache_id]["elem"],create__Delegate_CP(pThis,function(e){this.doonchange(e);}));window[pThis._cache_id]["elem"].onpropertychange=this.doonpropertychange;}
if(pThis.isControlInitialized==true){return!pThis.isMaskNull;}
if(pThis.isMaskNull==true)
return false;window[pThis._cache_id]["elem"].onbeforepaste=create__Delegate_CP(pThis,function(e){this.dobeforepaste(e);});window[pThis._cache_id]["elem"].onpaste=create__Delegate_CP(pThis,function(e){this.dopaste(e);});pThis.isControlInitialized=true;pThis.updateControlText();pThis.doClientEvent("OnClientInit");return true;}
this._prev_doonpropertychange=-1;this.doonpropertychange=function(){if(window.event!=null&&window.event.propertyName!=null){if(event.propertyName=="value"&&pThis.isControlFocused==false){var aCurDtMs=new Date().getTime();if(pThis._prev_doonpropertychange==-1){pThis._prev_doonpropertychange=aCurDtMs;}
if((pThis._prev_doonpropertychange+1000)<aCurDtMs){pThis._prev_doonpropertychange=aCurDtMs;pThis.doonchange();}}}}
this.additionalPostData="";this.putPostDataValue=function(aKey,aValue,aNeedRemoveKey,aSkipEscape){if(aNeedRemoveKey!=undefined&&aNeedRemoveKey==true){}
if(aSkipEscape!=undefined&&aSkipEscape==true){}else{aValue=escape(""+aValue+"");}
pThis.additionalPostData+="|="+aKey+"|="+aValue;pThis.updatePostData();}
this.updatePostData=function(){if(pThis.isControlInitialized==false){window[pThis._cache_id]["ViewStateElem"].value="Text|="+escape(window[pThis._cache_id]["elem"].value);return;}
window[pThis._cache_id]["ViewStateElem"].value=pThis.C1MaskedTextProvider_.get_PostDataString()+pThis.additionalPostData;}
this.getInputElement=function(){return window[pThis._cache_id]["elem"];}
this.__updateControlText__prevTextValue__="";this._raiseTextChangedIfNeeded=function(){var aCurValue=window[pThis._cache_id]["elem"].value;if(pThis.__updateControlText__prevTextValue__!=aCurValue){pThis.doClientEvent("OnClientTextChanged");pThis.__updateControlText__prevTextValue__=window[pThis._cache_id]["elem"].value;}}
this.__updateControlText__prevDateValue__=null;this._raiseDateChangedIfNeeded=function(){if(pThis.C1MaskedTextProvider_.get_date!=undefined){var aDtToCmp=pThis.C1MaskedTextProvider_.get_date();if(aDtToCmp instanceof Date){aDtToCmp=aDtToCmp.getTime();}
if(pThis.__updateControlText__prevDateValue__!=null&&pThis.__updateControlText__prevDateValue__!=aDtToCmp){pThis._raiseOnClientDateChanged();}
pThis.__updateControlText__prevDateValue__=aDtToCmp;}}
this.updateControlText=function(aNeedToRestoreSelection,aCalledOnBlur){if(!pThis.IsInitialized())
return false;if(aNeedToRestoreSelection==undefined||aNeedToRestoreSelection==null||aNeedToRestoreSelection==false){window[pThis._cache_id]["elem"].value=pThis.C1MaskedTextProvider_.ToString(!pThis.get_IsPassword(),pThis.HidePromptOnLeaveValue==true?pThis.isControlFocused:true,true);}else{var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();window[pThis._cache_id]["elem"].value=pThis.C1MaskedTextProvider_.ToString(!pThis.get_IsPassword(),pThis.HidePromptOnLeaveValue==true?pThis.isControlFocused:true,true);if(window[pThis._cache_id]["elem"].disabled)
return;pThis.selectText(sel.start,sel.end);prevUpDownPos=sel.start;}
pThis._raiseTextChangedIfNeeded();pThis._raiseDateChangedIfNeeded();if(pThis.C1MaskedTextProvider_.checkAndRepairBounds!=undefined){if(!pThis.C1MaskedTextProvider_.checkAndRepairBounds(false)){pThis.doClientEvent("OnClientValueBoundsExceeded");}}
pThis.updatePostData();}
this.selectText=function(begIndex,endIndex){if(window[pThis._cache_id]["elem"].disabled)
return;if(begIndex==undefined){begIndex=0;endIndex=window[pThis._cache_id]["elem"].value.length;}else if(endIndex==undefined){endIndex=begIndex;}
var selection=new Selection(window[pThis._cache_id]["elem"]);selection.setSelectionRange(begIndex,endIndex);}
this.deleteSelectedText=function(deleteByBackSpace){var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();sel.end=sel.end-1;if(sel.end<sel.start)
sel.end=sel.start;if(deleteByBackSpace!=undefined&&deleteByBackSpace==true&&sel.end==sel.start){if(sel.end>=1){sel.end=sel.end-1;sel.start=sel.start-1;}else{return;}}
var resultHint1=new MaskedTextResultHint();var aResult1=pThis.C1MaskedTextProvider_.RemoveAt(sel.start,sel.end,resultHint1);pThis.updateControlText();pThis.selectText(resultHint1.testPosition);}
this.fireIvalidInputEvent=function(resultHint){pThis.doClientEvent("OnClientInvalidInput");if(pThis.isInvalidInputColorShowing==false){if(pThis.InvalidInputColor!=undefined&&pThis.InvalidInputColor!=""){pThis.isInvalidInputColorShowing=true;var aPrevColor=window[pThis._cache_id]["elem"].style.color;setTimeout(function(){window[pThis._cache_id]["elem"].style.color=aPrevColor;pThis.isInvalidInputColorShowing=false;},100);try{window[pThis._cache_id]["elem"].style.color=pThis.InvalidInputColor;}catch(e){pThis.InvalidInputColor="";}}}}
this.isAllowEditControlValueByUser=function(){if((window[pThis._cache_id]["elem"].readOnly)||(window[pThis._cache_id]["elem"].disabled)){return false;}
return true;}
this.showEnumHintIfNeeded=function(aIndex){if(pThis.ShowHintForEnumPartsValue==false||pThis.C1MaskedTextProvider_.get_HaveEnumParts()==false)
return false;if(pThis._isInputFilterDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
if(pThis._isUserInputDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
var aEnumObject=pThis.C1MaskedTextProvider_.Get_EnumPartObjectForPosition(aIndex);if(aEnumObject!=null){if(!pThis.isAllowEditControlValueByUser()){return false;}
if(aEnumObject.EnumPartType_!=EnumPartType.Degit){pThis.EnumPartsHelperWindow_.show(aEnumObject,1);}else{pThis.EnumPartsHelperWindow_.show(aEnumObject,1);}}else{pThis.doHideEnumarationsHint(1);}}
this.doHideEnumarationsHint=function(aHideInterval){if(aHideInterval==undefined)
aHideInterval=300;pThis.EnumPartsHelperWindow_.hide(aHideInterval);}
this.selectEditablePart=function(){return false;}
this.doonmousedown=function(e){var e=e||window.event;pThis.doClientEvent("OnClientMouseDown",new Array(e));return true;}
this.doonmouseup=function(e){var e=e||window.event;if(pThis.isControlInitialized==false)
return;pThis.doClientEvent("OnClientMouseUp",new Array(e));if(window[pThis._cache_id]["elem"].disabled)
return true;var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.showEnumHintIfNeeded(sel.start);pThis.selectEditablePart();prevUpDownPos=sel.start;return false;}
this.doonmouseover=function(e){var e=e||window.event;pThis.doClientEvent("OnClientMouseOver",new Array(e));pThis.doStopUpDownButton();return true;}
this.doonmouseout=function(e){var e=e||window.event;pThis.doClientEvent("OnClientMouseOut",new Array(e));pThis.doStopUpDownButton();return true;}
this.doonchange=function(){if(pThis._cache_id==null||window[pThis._cache_id]==null||window[pThis._cache_id]["elem"]==null){return false;}
var sVal=window[pThis._cache_id]["elem"].value;var sText=pThis.get_Text();if(sText!=sVal){sText=pThis.get_TextWithPrompts();if(sText!=sVal){sText=pThis.get_TextWithPromptAndLiterals();if(sText!=sVal){pThis.set_Text(sVal);var aResult=sText!=pThis.get_TextWithPromptAndLiterals();if(pThis._isInputFilterDisabled==true){if(aResult==false){pThis.fireIvalidInputEvent();}}
return aResult;}}}
return false;}
this.tagwait_need_blur=false;this._focusNotCalledFirstTime=0;this.dofocus=function(e){if(pThis._isUserInputDisabled==true)
return;if(pThis.breakRepeatingUpDownButtons==false){if(pThis.isControlFocused!=true){pThis.isControlFocused=true;pThis.doClientEvent("OnClientFocus");}
return;}
if(pThis.isControlInitialized==false)
return;pThis.tagwait_need_blur=false;if(!pThis.isAllowEditControlValueByUser()){return false;}
if(pThis._focusNotCalledFirstTime==0){pThis._focusNotCalledFirstTime=new Date().getTime();}
if(pThis.isControlFocused!=true){pThis.isControlFocused=true;window.setTimeout(function(){if(pThis.isControlFocused==true){pThis.doClientEvent("OnClientFocus");}},50);if(pThis.HidePromptOnLeaveValue==true){pThis.updateControlText();if(pThis.selectEditablePart()!=true){var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.selectText(sel.start);}}}
return true;}
this.doblur=function(e){if(pThis._isUserInputDisabled==true)
return;pThis.doHideEnumarationsHint();if(pThis.breakRepeatingUpDownButtons==false){window[pThis._cache_id]["elem"].focus();if(prevUpDownPos!=-1)
pThis.selectText(prevUpDownPos);return;}
if(pThis.isControlInitialized==false)
return;if(pThis._isInputFilterDisabled==true){pThis.validateInput();}
if(pThis.isControlFocused==false)
return true;pThis.tagwait_need_blur=true;window.setTimeout(function(){if(pThis.tagwait_need_blur!=true)
return;pThis.tagwait_need_blur=false;pThis.isControlFocused=false;if(pThis.C1MaskedTextProvider_.checkAndRepairBounds!=undefined){if(!pThis.C1MaskedTextProvider_.checkAndRepairBounds(true)){pThis.updateControlText();}}
pThis.doonchange();pThis.updateControlText(null,true);window.setTimeout(function(){if(pThis.isControlFocused==false)
pThis.doClientEvent("OnClientBlur");},50);},100);return true;}
var prevUpDownPos=-1;this.doUpButton=function(aNeedRepeating){if(!pThis.isAllowEditControlValueByUser()){return;}
if(aNeedRepeating==undefined)
aNeedRepeating=false;if(aNeedRepeating&&pThis.breakRepeatingUpDownButtons==true)
return;var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();var resultHint=new MaskedTextResultHint();if(pThis._focusNotCalledFirstTime!=-9&&(new Date().getTime()-pThis._focusNotCalledFirstTime)<600){pThis._focusNotCalledFirstTime=-9;prevUpDownPos=0;}
if(prevUpDownPos==-1){prevUpDownPos=sel.start;}else{sel.start=prevUpDownPos;}
resultHint.testPosition=sel.start;pThis.C1MaskedTextProvider_.doIncrementEnumerationPart(sel.start,resultHint,pThis._increment);pThis.updateControlText();prevUpDownPos=resultHint.testPosition;pThis.selectText(resultHint.testPosition);pThis.selectEditablePart();if(aNeedRepeating&&pThis.breakRepeatingUpDownButtons!=true){var aInterval=pThis.calculateUpDownButtonsRepeatingInterval();window.setTimeout(function(){pThis.doUpButton(true);},aInterval);}}
this.doDownButton=function(aNeedRepeating){if(!pThis.isAllowEditControlValueByUser()){return;}
if(aNeedRepeating==undefined)
aNeedRepeating=false;if(aNeedRepeating&&pThis.breakRepeatingUpDownButtons==true)
return;var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();var resultHint=new MaskedTextResultHint();if(prevUpDownPos==-1){prevUpDownPos=sel.start;}else{sel.start=prevUpDownPos;}
resultHint.testPosition=sel.start;pThis.C1MaskedTextProvider_.doDecrementEnumerationPart(sel.start,resultHint,pThis._increment);pThis.updateControlText();prevUpDownPos=resultHint.testPosition;pThis.selectText(resultHint.testPosition);pThis.selectEditablePart();if(aNeedRepeating&&pThis.breakRepeatingUpDownButtons!=true){var aInterval=pThis.calculateUpDownButtonsRepeatingInterval();window.setTimeout(function(){pThis.doDownButton(true);},aInterval);}}
this.calculateUpDownButtonsRepeatingInterval=function(){var aInterval=400;pThis.repeatingUpDownCount++;if(pThis.repeatingUpDownCount>10)
aInterval=50;else if(pThis.repeatingUpDownCount>4)
aInterval=100;else if(pThis.repeatingUpDownCount>2)
aInterval=200;return aInterval;}
this.breakRepeatingUpDownButtons=true;this.repeatingUpDownCount=0;this.doStopUpDownButton=function(){pThis.breakRepeatingUpDownButtons=true;pThis.repeatingUpDownCount=0;}
this.dobeforepaste=function(){var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.beforePasteSelection=sel;pThis.beforePasteSelection.controlValueLength_=window[pThis._cache_id]["elem"].value.length;}
this.dopaste=function(){window.setTimeout(function(){if(!pThis.doonchange()){}},1);}
this.dokeyup=function(e){var e=e||window.event;var k=e.which||e.keyCode;pThis.doClientEvent("OnClientKeyUp",new Array(k,e));if(!pThis.IsInitialized()){pThis.updatePostData();return;}
if(k==27&&this._prevDownKeyCode==k){pThis.doonchange();}
if(pThis._isInputFilterDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
if(pThis._isUserInputDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.showEnumHintIfNeeded(sel.start);pThis.cancelBrowserResponseOnEvent(e);return false;}
this.dokeypress=function(e){prevUpDownPos=-1;var e=e||window.event;var k=e.which||e.keyCode;if(pThis.isControlInitialized==false)
return;pThis.doClientEvent("OnClientKeyPress",new Array(k,e));if(pThis._isInputFilterDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
if(pThis._isUserInputDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
if(e.ctrlKey){switch(k){case 118:pThis.dopaste();return;default:}}
if(e.ctrlKey||e.altKey){return;}
switch(k){case 112:case 113:case 114:case 115:case 116:case 117:if(this._prevDownKeyCode==k){return;}else{break;}
case 13:if(!pThis.HideEnterValue)
return;break;case 8:case 18:case 9:case 35:case 36:case 37:case 38:case 39:case 40:if(this._prevDownKeyCode==k){return;}else{break;}
case 46:case 27:if(this._prevDownKeyCode==k){pThis.cancelBrowserResponseOnEvent(e);return false;}else{break;}
case 16:return;}
if(!pThis.isAllowEditControlValueByUser()){return false;}
var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();var chValue=String.fromCharCode(k);if(sel.start<sel.end){var resultHint1=new MaskedTextResultHint();var aResult1=pThis.C1MaskedTextProvider_.RemoveAt(sel.start,sel.end-1,resultHint1);}
pThis.showEnumHintIfNeeded(sel.start);var resultHint=new MaskedTextResultHint();var aOperationResult=pThis.C1MaskedTextProvider_.InsertAt(chValue,sel.start,resultHint);if(aOperationResult){pThis.updateControlText();pThis.selectText(resultHint.testPosition+1);}else{pThis.fireIvalidInputEvent(resultHint);}
pThis.cancelBrowserResponseOnEvent(e);return false;}
this._prevDownKeyCode=-1;this.dokeydown=function(e){prevUpDownPos=-1;var e=e||window.event;var k=e.which||e.keyCode;this._prevDownKeyCode=k;if(pThis.isControlInitialized==false)
return;pThis.doClientEvent("OnClientKeyDown",new Array(k,e));if(pThis._isUserInputDisabled==true){pThis.cancelBrowserResponseOnEvent(e);return false;return;}
switch(k){case 38:if(pThis._isInputFilterDisabled==true){pThis.validateInput();}
pThis.doUpButton();pThis.cancelBrowserResponseOnEvent(e);return false;case 40:if(pThis._isInputFilterDisabled==true){pThis.validateInput();}
pThis.doDownButton();pThis.cancelBrowserResponseOnEvent(e);return false;}
if(pThis._isInputFilterDisabled==true){pThis._raiseTextChangedIfNeeded();return;}
if(e.ctrlKey){switch(k){case 45:case 67:return true;case 86:pThis.dobeforepaste();return;default:}}
if((e.ctrlKey||e.altKey)){return false;}
switch(k){case 112:case 113:case 114:case 115:case 116:case 117:return;case 9:case 20:case 35:case 36:case 17:break;case 37:if(!e.shiftKey){var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.showEnumHintIfNeeded(sel.start-1);}
return;case 39:if(!e.shiftKey){var selection=new Selection(window[pThis._cache_id]["elem"]);var sel=selection.create();pThis.showEnumHintIfNeeded(sel.start+1);}
return;case 8:pThis.deleteSelectedText(true);pThis.cancelBrowserResponseOnEvent(e);return;case 46:pThis.deleteSelectedText();pThis.cancelBrowserResponseOnEvent(e);return false;case 13:if(!pThis.HideEnterValue)
return;case 27:return;case 33:case 34:case 18:pThis.cancelBrowserResponseOnEvent(e);return false;case 16:return;}}
this.cancelBrowserResponseOnEvent=function(e)
{if(e==null)
e=window.event;if(e==null)
return false;if(e.stopPropagation!=null)e.stopPropagation();if(e.preventDefault!=null)e.preventDefault();e.cancelBubble=true;e.returnValue=false;return false;}
this.setStyleFromCssString=function(aHtmlNode,aCssString){if(aHtmlNode!=null&&aHtmlNode!=undefined)
aHtmlNode.style.cssText=aCssString;}
this._hideC1WebCalendar=function(){var aCal=window[pThis._webCalendarObjId];if(aCal!=null){if(aCal.IsPopupShowing()){aCal.Close();return true;}}
return false;}
this._popupOrHideC1WebCalendar=function(aCal){if(!pThis.isAllowEditControlValueByUser()){return;}
if(pThis._webCalendarObjId!=null){var aCal=window[pThis._webCalendarObjId];if(aCal!=null){if(aCal.PopupMode!=null&&aCal.PopupMode==false)
return;if(pThis._hideC1WebCalendar())
return;var d=pThis.get_Date();aCal.UnSelectAll();aCal.SelectDate(d);aCal.DisplayDate=d;if(pThis._webCalendarPosition==null)
pThis._webCalendarPosition="NotChange";switch(pThis._webCalendarPosition.toLowerCase()){case"near":aCal.PopupSetting.Dock=window.c1_dock_lefttop;break;case"far":aCal.PopupSetting.Dock=window.c1_dock_righttop;break;case"above":aCal.PopupSetting.Dock=window.c1_dock_topleft;break;case"below":aCal.PopupSetting.Dock=window.c1_dock_bottomleft;break;}
aCal.PopupBeside(window[pThis._cache_id]["elemTbl"]);}}}
this._C1WebCalendar_SelChange=function(calendar,seltype,seldates){if(calendar)
{pThis.set_Date(calendar.SelectedDate);}}
this.initializeImageButtonEvents=function(aImgTag,aTdTag,aImagesArr,aStylesArr,aMousePressedFunction,aIsCustomButton){var aUId="iibe"+Generate__UniqIdWebInputUsage();if(aImgTag==null){try{aImgTag=new Image();}catch(ex){}}
window[pThis._cache_id][aUId+"_OldImg"]=aImgTag;window[pThis._cache_id][aUId+"_TdTag"]=aTdTag;aImgTag=null;aTdTag=null;window[pThis._cache_id][aUId+"_TdTag"].aInputObjGlobalObjId=pThis._objId;window[pThis._cache_id][aUId+"_TdTag"].firstChild._c1_dom_isTargetToParentNode=true;window[pThis._cache_id][aUId+"_TdTag"].firstChild.aInputObjGlobalObjId=pThis._objId;window[pThis._cache_id][aUId+"_OldImg"].aInputObjGlobalObjId=pThis._objId;if(aImagesArr!=null){for(var i=0;i<aImagesArr.length;i++){if(aImagesArr[i]!=null)
aImagesArr[i].aInputObjGlobalObjId=pThis._objId;}}
var aCurState=0;window[pThis._cache_id][aUId+"_TdTag"].onmouseover=function(ev){pThis.doStopUpDownButton();aCurState=1;pThis.setStyleFromCssString(window[pThis._cache_id][aUId+"_TdTag"],aStylesArr[1]);var aNewImg=aImagesArr[1];if(aNewImg!=window[pThis._cache_id][aUId+"_OldImg"]&&(aNewImg!=null)){try{window[pThis._cache_id][aUId+"_TdTag"].replaceChild(aNewImg,window[pThis._cache_id][aUId+"_OldImg"]);window[pThis._cache_id][aUId+"_OldImg"]=aNewImg;}catch(exInImg){}}}
window[pThis._cache_id][aUId+"_TdTag"].onmouseout=function(ev){pThis.doStopUpDownButton();aCurState=0;window.setTimeout(function(){if(aCurState!=0){return;}
pThis.setStyleFromCssString(window[pThis._cache_id][aUId+"_TdTag"],aStylesArr[0]);var aNewImg=aImagesArr[0];if(aNewImg!=window[pThis._cache_id][aUId+"_OldImg"]&&(aNewImg!=null)){try{window[pThis._cache_id][aUId+"_TdTag"].replaceChild(aNewImg,window[pThis._cache_id][aUId+"_OldImg"]);window[pThis._cache_id][aUId+"_OldImg"]=aNewImg;}catch(exInImg){}}},1);}
window[pThis._cache_id][aUId+"_TdTag"].onmousedown=function(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;aCurState=2;pThis.setStyleFromCssString(window[pThis._cache_id][aUId+"_TdTag"],aStylesArr[2]);var aNewImg=aImagesArr[2];if(aNewImg!=window[pThis._cache_id][aUId+"_OldImg"]&&(aNewImg!=null)){try{window[pThis._cache_id][aUId+"_TdTag"].replaceChild(aNewImg,window[pThis._cache_id][aUId+"_OldImg"]);window[pThis._cache_id][aUId+"_OldImg"]=aNewImg;}catch(exInImg){}}
if(aMousePressedFunction!=undefined){if(pThis.isControlFocused!=true){try{if(pThis._isUserInputDisabled!=true){pThis.isControlFocused=true;window[pThis._cache_id]["elem"].focus();pThis.doClientEvent("OnClientFocus");}}catch(ex){}}
if(aMousePressedFunction=="!spin_up"){pThis.breakRepeatingUpDownButtons=false;pThis.doUpButton(true);}else if(aMousePressedFunction=="!spin_down"){pThis.breakRepeatingUpDownButtons=false;pThis.doDownButton(true);}else if(aMousePressedFunction!=""){pThis.doClientEvent(aMousePressedFunction);}}}
window[pThis._cache_id][aUId+"_TdTag"].onmouseup=function(e){e=e||window.event;if(e==null)return;var target=e.srcElement||e.target;pThis.doStopUpDownButton();aCurState=1;pThis.setStyleFromCssString(window[pThis._cache_id][aUId+"_TdTag"],aStylesArr[1]);var aNewImg=aImagesArr[1];if(aNewImg!=window[pThis._cache_id][aUId+"_OldImg"]&&(aNewImg!=null)){try{window[pThis._cache_id][aUId+"_TdTag"].replaceChild(aNewImg,window[pThis._cache_id][aUId+"_OldImg"]);window[pThis._cache_id][aUId+"_OldImg"]=aNewImg;}catch(exInImg){}}
if(aIsCustomButton==true){if(pThis._pendCustBtnClickDel==null){pThis._pendCustBtnClickDel=create__Delegate_CP(pThis,pThis._riseCustomBtnClick);}
window.setTimeout(pThis._pendCustBtnClickDel,5)}
if(aIsCustomButton==true){pThis._popupComboList();pThis._popupOrHideC1WebCalendar();}}
try{window[pThis._cache_id][aUId+"_TdTag"].parentNode.parentNode.onmouseout=function(){pThis.doStopUpDownButton();};window[pThis._cache_id][aUId+"_TdTag"].parentNode.parentNode.onmouseover=function(){pThis.doStopUpDownButton();};}catch(ex){}}
this.checkAndRepairBtnImageSizeBounds=function(aImage,aIsCustomButton,aButtonWidth,aCtrlHeight){try{if(aCtrlHeight==undefined)
return;var cs=parseFloat(window[pThis._cache_id]["elemTbl"].style.cellSpacing*1);if(isNaN(cs))
cs=0;aCtrlHeight=aCtrlHeight*1-cs*2-(aIsCustomButton==true?0:1);var del=1;if(!aIsCustomButton){del=2;}
if(aImage!=undefined){if(!isNaN(parseFloat(aImage.height))&&aImage.height>aCtrlHeight/del){aImage.height=aCtrlHeight/del;}
if(aButtonWidth!=undefined&&!isNaN(parseFloat(aImage.width))){if(aImage.width>aButtonWidth-2){aImage.width=aButtonWidth-2;}}}}catch(ex){}}
this.initBtn=function(aTdImgIdPostfix,aImgIdPostfix,aHoverImageUrl,aPressedImageUrl,aBtnHoverStyle,aBtnPressedStyle,aMousePressedFunction,aIsCustomButton,aButtonWidth,aControlHeight){var aImgTag=get_element_by___id(pThis.id+aImgIdPostfix);var aTdTag=get_element_by___id(pThis.id+aTdImgIdPostfix);if(aTdTag!=null){aTdTag.style.cursor="default";aBtnHoverStyle="cursor:default;"+aBtnHoverStyle;aBtnPressedStyle="cursor:default;"+aBtnPressedStyle;}
var aHoverImage=null;if(aHoverImageUrl!=undefined&&aHoverImageUrl!=""){aHoverImage=new Image();aHoverImage.src=aHoverImageUrl;}
var aPressedImage=null;if(aPressedImageUrl!=undefined&&aPressedImageUrl!=""){aPressedImage=new Image();aPressedImage.src=aPressedImageUrl;}
try{this.checkAndRepairBtnImageSizeBounds(aImgTag,aIsCustomButton,aButtonWidth,aControlHeight);this.checkAndRepairBtnImageSizeBounds(aHoverImage,aIsCustomButton,aButtonWidth,aControlHeight);this.checkAndRepairBtnImageSizeBounds(aPressedImage,aIsCustomButton,aButtonWidth,aControlHeight);}catch(ex){}
pThis[pThis.id+"btnimagesArr_"+aImgIdPostfix]=new Array();pThis[pThis.id+"btnimagesArr_"+aImgIdPostfix].push(aImgTag);pThis[pThis.id+"btnimagesArr_"+aImgIdPostfix].push(aHoverImage);pThis[pThis.id+"btnimagesArr_"+aImgIdPostfix].push(aPressedImage);pThis[pThis.id+"btnstylesArr_"+aImgIdPostfix]=new Array();pThis[pThis.id+"btnstylesArr_"+aImgIdPostfix].push(aTdTag.style.cssText);pThis[pThis.id+"btnstylesArr_"+aImgIdPostfix].push(aBtnHoverStyle);pThis[pThis.id+"btnstylesArr_"+aImgIdPostfix].push(aBtnPressedStyle);pThis.initializeImageButtonEvents(aImgTag,aTdTag,pThis[pThis.id+"btnimagesArr_"+aImgIdPostfix],pThis[pThis.id+"btnstylesArr_"+aImgIdPostfix],aMousePressedFunction,aIsCustomButton);}
this.cutomButtonImagesArr;this.initCustomButton=function(aHoverImageUrl,aPressedImageUrl,aBtnHoverStyle,aBtnPressedStyle,aButtonWidth,aControlHeight){pThis.initBtn("_cb_td","_cb_img",aHoverImageUrl,aPressedImageUrl,aBtnHoverStyle,aBtnPressedStyle,"",true,aButtonWidth,aControlHeight);}
this.initSpinButtons=function(aHoverImageUrlUp,aHoverImageUrlDown,aPressedImageUrlUp,aPressedImageUrlDown,aBtnUpHoverStyle,aBtnUpPressedStyle,aBtnDownHoverStyle,aBtnDownPressedStyle,aButtonWidth,aControlHeight){pThis.initBtn("_sbu_td","_sbu_img",aHoverImageUrlUp,aPressedImageUrlUp,aBtnUpHoverStyle,aBtnUpPressedStyle,"!spin_up",false,aButtonWidth);pThis.initBtn("_sbd_td","_sbd_img",aHoverImageUrlDown,aPressedImageUrlDown,aBtnDownHoverStyle,aBtnDownPressedStyle,"!spin_down",false,aButtonWidth,aControlHeight);}
this._raiseOnClientDateChanged=function(){if(pThis._webCalendarObjId!=null&&pThis._webCalendarObjId!=""){var aCal=window[pThis._webCalendarObjId];if(aCal!=null){var d=pThis.get_Date();aCal.UnSelectAll();aCal.SelectDate(d);var d2=aCal.GetDisplayDate();if(d2.getMonth()!=d.getMonth()||d2.getYear()!=d.getYear()){aCal.SwapToDate(d);}}}
pThis.doClientEvent("OnClientDateChanged");}
this._riseCustomBtnClick=function(){pThis.doClientEvent("OnClientCustomButtonClick");}
this._comboListWidth=-1;this._comboListHeight=-1;this._comboItemsArr=null;this._smartInputMode=true;this._startYear=1950;this._showNullText=false;this._increment=1;this._nullText="Empty";this._webCalendarObjId="";this._webCalendarPosition="NotChange";this._objId=null;}
function Selection(textareaElement){this.element=textareaElement;}
Selection.prototype.setSelectionRange=function(start,end){if(document.selection!=null&&this.element.selectionStart==null){var range=this.element.createTextRange();range.collapse(true);range.moveStart("character",start);range.moveEnd("character",end-start);range.select();}else{this.element.setSelectionRange(start,end);}};Selection.prototype.create=function(){if(document.selection!=null&&this.element.selectionStart==null){return this._ieGetSelection();}else{return this._mozillaGetSelection();}}
Selection.prototype._mozillaGetSelection=function(){return{start:this.element.selectionStart,end:this.element.selectionEnd};}
Selection.prototype._ieGetSelection=function(){var aStart=0;var aEnd=0;try{aStart=Math.abs(document.selection.createRange().moveStart("character",-1000000));aEnd=aStart;}catch(e){}
try{aEnd=aStart+document.selection.createRange().text.length;}catch(e){}
var result={};result.start=aStart;result.end=aEnd;return result;}