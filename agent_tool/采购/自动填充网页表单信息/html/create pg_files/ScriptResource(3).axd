
function trueOR(n1,n2){return((n1>>>1|n2>>>1)*2+(n1&1|n2&1));}
EnumPartType=new Object();EnumPartType.Symbol=1;EnumPartType.Degit=2;CharType=new Object();CharType.EditOptional=1;CharType.EditRequired=2;CharType.Literal=8;CharType.Modifier=0x10;CharType.Separator=4;CaseConversion=new Object();CaseConversion.None=0;CaseConversion.ToLower=1;CaseConversion.ToUpper=2;function MaskedTextResultHint(){this.AlphanumericCharacterExpected=-2;this.AsciiCharacterExpected=-1;this.CharacterEscaped=1;this.DigitExpected=-3;this.InvalidInput=-51;this.LetterExpected=-4;this.NoEffect=2;this.NonEditPosition=-54;this.PositionOutOfRange=-55;this.PromptCharNotAllowed=-52;this.SideEffect=3;this.SignedDigitExpected=-5;this.Success=4;this.UnavailableEditPosition=-53;this.Unknown=0;this.hint=this.Unknown;this.testPosition=-1;this.Clone=function(){var aMaskedTextResultHint=new MaskedTextResultHint();aMaskedTextResultHint.hint=this.hint;aMaskedTextResultHint.testPosition=this.testPosition;return aMaskedTextResultHint;}}
function CultureInfo(){this.NumberFormat=new Object();this.NumberFormat.CurrencySymbol="rub.";this.NumberFormat.NumberGroupSeparator=",";this.NumberFormat.NumberDecimalSeparator=".";this.DateTimeFormat=new Object();this.DateTimeFormat.DateSeparator="/";this.DateTimeFormat.TimeSeparator=":";this.TextInfo=new Object();this.TextInfo.ToLower=function(input){return input.toLowerCase();}
this.TextInfo.ToUpper=function(input){return input.toUpperCase();}}
function CharDescriptor(maskPos,charType)
{this.CaseConversion=CaseConversion.None;this.CharType=charType;this.IsAssigned=false;this.MaskPosition=maskPos;this.EnumPartObject=null;}
function set_CharacterInString(input,ch,position){ch=ch+"";if(position>=input.length||position<0)
return input;var sResult="";sResult=input.substring(0,position)+ch+input.substring(position+ch.length);return sResult;}
function C1CharactersValidator(aCultureInfo){this.culture=aCultureInfo;this.UTFPunctuationsString_=' \u0021 \u0022 \u0023 \u0025 \u0026 \u0027 \u0028 \u0029 \u002A \u002C \u002D \u002E \u002F \u003A \u003B \u003F \u0040 \u005B \u005C \u005D \u007B \u007D \u00A1 \u00AB \u00AD \u00B7 \u00BB \u00BF \u037E \u0387 \u055A \u055B \u055C \u055D \u055E \u055F \u0589 \u058A \u05BE \u05C0 \u05C3 \u05F3 \u05F4 \u060C \u061B \u061F \u066A \u066B \u066C \u066D \u06D4 \u0700 \u0701 \u0702 \u0703 \u0704 \u0705 \u0706 \u0707 \u0708 \u0709 \u070A \u070B \u070C \u070D \u0964 \u0965 \u0970 \u0DF4 \u0E4F \u0E5A \u0E5B \u0F04 \u0F05 \u0F06 \u0F07 \u0F08 \u0F09 \u0F0A \u0F0B \u0F0C \u0F0D \u0F0E \u0F0F \u0F10 \u0F11 \u0F12 \u0F3A \u0F3B \u0F3C \u0F3D \u0F85 \u104A \u104B \u104C \u104D \u104E \u104F \u10FB \u1361 \u1362 \u1363 \u1364 \u1365 \u1366 \u1367 \u1368 \u166D \u166E \u169B \u169C \u16EB \u16EC \u16ED \u17D4 \u17D5 \u17D6 \u17D7 \u17D8 \u17D9 \u17DA \u17DC \u1800 \u1801 \u1802 \u1803 \u1804 \u1805 \u1806 \u1807 \u1808 \u1809 \u180A \u2010 \u2011 \u2012 \u2013 \u2014 \u2015 \u2016 \u2017 \u2018 \u2019 \u201A \u201B \u201C \u201D \u201E \u201F \u2020 \u2021 \u2022 \u2023 \u2024 \u2025 \u2026 \u2027 \u2030 \u2031 \u2032 \u2033 \u2034 \u2035 \u2036 \u2037 \u2038 \u2039 \u203A \u203B \u203C \u203D \u203E \u2041 \u2042 \u2043 \u2045 \u2046 \u2048 \u2049 \u204A \u204B \u204C \u204D \u207D \u207E \u208D \u208E \u2329 \u232A \u3001 \u3002 \u3003 \u3008 \u3009 \u300A \u300B \u300C \u300D \u300E \u300F \u3010 \u3011 \u3014 \u3015 \u3016 \u3017 \u3018 \u3019 \u301A \u301B \u301C \u301D \u301E \u301F \u3030 \uFD3E \uFD3F \uFE30 \uFE31 \uFE32 \uFE35 \uFE36 \uFE37 \uFE38 \uFE39 \uFE3A \uFE3B \uFE3C \uFE3D \uFE3E \uFE3F \uFE40 \uFE41 \uFE42 \uFE43 \uFE44 \uFE49 \uFE4A \uFE4B \uFE4C \uFE50 \uFE51 \uFE52 \uFE54 \uFE55 \uFE56 \uFE57 \uFE58 \uFE59 \uFE5A \uFE5B \uFE5C \uFE5D \uFE5E \uFE5F \uFE60 \uFE61 \uFE63 \uFE68 \uFE6A \uFE6B \uFF01 \uFF02 \uFF03 \uFF05 \uFF06 \uFF07 \uFF08 \uFF09 \uFF0A \uFF0C \uFF0D \uFF0E \uFF0F \uFF1A \uFF1B \uFF1F \uFF20 \uFF3B \uFF3C \uFF3D \uFF5B \uFF5D \uFF61 \uFF62 \uFF63 \uFF64';this.UTFWhitespacesString_='\u0009 \u000B \u000C \u001F \u0020 \u00A0 \u1680 \u2000 \u2001 \u2002 \u2003 \u2004 \u2005 \u2006 \u2007 \u2008 \u2009 \u200A \u200B \u2028 \u202F \u3000';this.setCharcterInString=function(input,ch,position){if(position>=input.length||position<0)
return input;var sResult="";sResult=input.substring(0,position)+ch+input.substring(position+1);return sResult;}
this.IsAscii=function(c)
{if(c>='!')
{return(c<='~');}
return false;}
this.IsAsciiLetter=function(c)
{if((c>='A')&&(c<='Z'))
{return true;}
if(c>='a')
{return(c<='z');}
return false;}
this.IsUpper=function(c)
{if(c.toUpperCase()==c)
return true;return false;}
this.IsLower=function(c)
{if(c.toLowerCase()==c)
return true;return false;}
this.IsAlphanumeric=function(c)
{if(!this.IsLetter(c))
{return this.IsDigit(c);}
return true;}
this.IsAciiAlphanumeric=function(c)
{if(((c<'0')||(c>'9'))&&((c<'A')||(c>'Z')))
{if(c>='a')
{return(c<='z');}
return false;}
return true;}
this.IsDigit=function(c)
{if(c>='0')
{return(c<='9');}
return false;}
this.IsLetter=function(c)
{c=""+c+"";if(c.match(/[\u0041-\u005a\u0061-\u007a\u00aa\u00b5\u00ba\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u021f\u0222-\u0233\u0250-\u02ad\u02b0-\u02b8\u02bb-\u02c1\u02d0\u02d1\u02e0-\u02e4\u02ee\u037a\u0386\u0388-\u038a\u038c\u038e-\u03a1\u03a3-\u03ce\u03d0-\u03d7\u03da-\u03f3\u0400-\u0481\u048c-\u04c4\u04c7\u04c8\u04cb\u04cc\u04d0-\u04f5\u04f8\u04f9\u0531-\u0556\u0559\u0561-\u0587\u05d0-\u05ea\u05f0-\u05f2\u0621-\u063a\u0640-\u064a\u0671-\u06d3\u06d5\u06e5\u06e6\u06fa-\u06fc\u0710\u0712-\u072c\u0780-\u07a5\u0905-\u0939\u093d\u0950\u0958-\u0961\u0985-\u098c\u098f\u0990\u0993-\u09a8\u09aa-\u09b0\u09b2\u09b6-\u09b9\u09dc\u09dd\u09df-\u09e1\u09f0\u09f1\u0a05-\u0a0a\u0a0f\u0a10\u0a13-\u0a28\u0a2a-\u0a30\u0a32\u0a33\u0a35\u0a36\u0a38\u0a39\u0a59-\u0a5c\u0a5e\u0a72-\u0a74\u0a85-\u0a8b\u0a8d\u0a8f-\u0a91\u0a93-\u0aa8\u0aaa-\u0ab0\u0ab2\u0ab3\u0ab5-\u0ab9\u0abd\u0ad0\u0ae0\u0b05-\u0b0c\u0b0f\u0b10\u0b13-\u0b28\u0b2a-\u0b30\u0b32\u0b33\u0b36-\u0b39\u0b3d\u0b5c\u0b5d\u0b5f-\u0b61\u0b85-\u0b8a\u0b8e-\u0b90\u0b92-\u0b95\u0b99\u0b9a\u0b9c\u0b9e\u0b9f\u0ba3\u0ba4\u0ba8-\u0baa\u0bae-\u0bb5\u0bb7-\u0bb9\u0c05-\u0c0c\u0c0e-\u0c10\u0c12-\u0c28\u0c2a-\u0c33\u0c35-\u0c39\u0c60\u0c61\u0c85-\u0c8c\u0c8e-\u0c90\u0c92-\u0ca8\u0caa-\u0cb3\u0cb5-\u0cb9\u0cde\u0ce0\u0ce1\u0d05-\u0d0c\u0d0e-\u0d10\u0d12-\u0d28\u0d2a-\u0d39\u0d60\u0d61\u0d85-\u0d96\u0d9a-\u0db1\u0db3-\u0dbb\u0dbd\u0dc0-\u0dc6\u0e01-\u0e30\u0e32\u0e33\u0e40-\u0e46\u0e81\u0e82\u0e84\u0e87\u0e88\u0e8a\u0e8d\u0e94-\u0e97\u0e99-\u0e9f\u0ea1-\u0ea3\u0ea5\u0ea7\u0eaa\u0eab\u0ead-\u0eb0\u0eb2\u0eb3\u0ebd\u0ec0-\u0ec4\u0ec6\u0edc\u0edd\u0f00\u0f40-\u0f47\u0f49-\u0f6a\u0f88-\u0f8b\u1000-\u1021\u1023-\u1027\u1029\u102a\u1050-\u1055\u10a0-\u10c5\u10d0-\u10f6\u1100-\u1159\u115f-\u11a2\u11a8-\u11f9\u1200-\u1206\u1208-\u1246\u1248\u124a-\u124d\u1250-\u1256\u1258\u125a-\u125d\u1260-\u1286\u1288\u128a-\u128d\u1290-\u12ae\u12b0\u12b2-\u12b5\u12b8-\u12be\u12c0\u12c2-\u12c5\u12c8-\u12ce\u12d0-\u12d6\u12d8-\u12ee\u12f0-\u130e\u1310\u1312-\u1315\u1318-\u131e\u1320-\u1346\u1348-\u135a\u13a0-\u13f4\u1401-\u166c\u166f-\u1676\u1681-\u169a\u16a0-\u16ea\u1780-\u17b3\u1820-\u1877\u1880-\u18a8\u1e00-\u1e9b\u1ea0-\u1ef9\u1f00-\u1f15\u1f18-\u1f1d\u1f20-\u1f45\u1f48-\u1f4d\u1f50-\u1f57\u1f59\u1f5b\u1f5d\u1f5f-\u1f7d\u1f80-\u1fb4\u1fb6-\u1fbc\u1fbe\u1fc2-\u1fc4\u1fc6-\u1fcc\u1fd0-\u1fd3\u1fd6-\u1fdb\u1fe0-\u1fec\u1ff2-\u1ff4\u1ff6-\u1ffc\u207f\u2102\u2107\u210a-\u2113\u2115\u2119-\u211d\u2124\u2126\u2128\u212a-\u212d\u212f-\u2131\u2133-\u2139\u3005\u3006\u3031-\u3035\u3041-\u3094\u309d\u309e\u30a1-\u30fa\u30fc-\u30fe\u3105-\u312c\u3131-\u318e\u31a0-\u31b7\u3400-\u4db5\u4e00-\u9fa5\ua000-\ua48c\uac00-\ud7a3\uf900-\ufa2d\ufb00-\ufb06\ufb13-\ufb17\ufb1d\ufb1f-\ufb28\ufb2a-\ufb36\ufb38-\ufb3c\ufb3e\ufb40\ufb41\ufb43\ufb44\ufb46-\ufbb1\ufbd3-\ufd3d\ufd50-\ufd8f\ufd92-\ufdc7\ufdf0-\ufdfb\ufe70-\ufe72\ufe74\ufe76-\ufefc\uff21-\uff3a\uff41-\uff5a\uff66-\uffbe\uffc2-\uffc7\uffca-\uffcf\uffd2-\uffd7\uffda-\uffdc]/)){return true;}
return false;}
this.IsLetterOrDigit=function(c)
{if(this.IsLetter(c))
return true;if(this.IsDigit(c))
return true;return false}
this.IsSymbol=function(c)
{var re=/[\u0024\u002b\u003c-\u003e\u005e\u0060\u007c\u007e\u00a2-\u00a9\u00ac\u00ae-\u00b1\u00b4\u00b6\u00b8\u00d7\u00f7\u02b9\u02ba\u02c2-\u02cf\u02d2-\u02df\u02e5-\u02ed\u0374\u0375\u0384\u0385\u0482\u06e9\u06fd\u06fe\u09f2\u09f3\u09fa\u0b70\u0e3f\u0f01-\u0f03\u0f13-\u0f17\u0f1a-\u0f1f\u0f34\u0f36\u0f38\u0fbe-\u0fc5\u0fc7-\u0fcc\u0fcf\u17db\u1fbd\u1fbf-\u1fc1\u1fcd-\u1fcf\u1fdd-\u1fdf\u1fed-\u1fef\u1ffd\u1ffe\u2044\u207a-\u207c\u208a-\u208c\u20a0-\u20af\u2100\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211e-\u2123\u2125\u2127\u2129\u212e\u2132\u213a\u2190-\u21f3\u2200-\u22f1\u2300-\u2328\u232b-\u237b\u237d-\u239a\u2400-\u2426\u2440-\u244a\u249c-\u24e9\u2500-\u2595\u25a0-\u25f7\u2600-\u2613\u2619-\u2671\u2701-\u2704\u2706-\u2709\u270c-\u2727\u2729-\u274b\u274d\u274f-\u2752\u2756\u2758-\u275e\u2761-\u2767\u2794\u2798-\u27af\u27b1-\u27be\u2800-\u28ff\u2e80-\u2e99\u2e9b-\u2ef3\u2f00-\u2fd5\u2ff0-\u2ffb\u3004\u3012\u3013\u3020\u3036\u3037\u303e\u303f\u309b\u309c\u3190\u3191\u3196-\u319f\u3200-\u321c\u322a-\u3243\u3260-\u327b\u327f\u328a-\u32b0\u32c0-\u32cb\u32d0-\u32fe\u3300-\u3376\u337b-\u33dd\u33e0-\u33fe\ua490-\ua4a1\ua4a4-\ua4b3\ua4b5-\ua4c0\ua4c2-\ua4c4\ua4c6\ufb29\ufe62\ufe64-\ufe66\ufe69\uff04\uff0b\uff1c-\uff1e\uff3e\uff40\uff5c\uff5e\uffe0-\uffe6\uffe8-\uffee\ufffc\ufffd]/;return re.test(c);}
this.IsPunctuation=function(c)
{if(this.UTFPunctuationsString_.indexOf(c)!=-1)
return true;else
return false;}
this.IsPrintableChar=function(c)
{if((!this.IsLetterOrDigit(c)&&!this.IsPunctuation(c))&&!this.IsSymbol(c))
{return(c==' ');}
return true;}}
function EnumPart(id,arr,aEnumPartType,beginIndex,aParentTextProvider){this._parentTextProvider=aParentTextProvider;this.id=id;this.arr=arr;this.EnumPartType_=aEnumPartType;this.maxLen=0;this.curValueIndex=0;this.currentDigitValue=0;this.minDigitValue=0;this.maxDigitValue=0;this.beginIndex=beginIndex;this.realBeginIndex=-1;this.curLen=0;this.initialValue=0;var aMaxLen=0;for(var i=0;i<arr.length;i++)
{if(i==0&&this.EnumPartType_==EnumPartType.Degit){this.currentDigitValue=arr[i]*1;this.initialValue=this.currentDigitValue;this.minDigitValue=parseInt(arr[i]);this.maxDigitValue=parseInt(arr[i]);if(this.maxDigitValue>=Number.MAX_VALUE){}}else if(i>=1&&this.EnumPartType_==EnumPartType.Degit){this.maxDigitValue=parseInt(arr[i]);}
var aCurLen=arr[i].length;if(arr[i].length>0&&arr[i].charAt(0)=='*')
{arr[i]=arr[i].substr(1);this.curValueIndex=i;this.initialValue=this.curValueIndex;aCurLen=aCurLen-1;}
aMaxLen=aCurLen>aMaxLen?aCurLen:aMaxLen;}
this.maxLen=aMaxLen;this.ApplyFormatToEnumValue=function(aEnumValue,aCalculateHidenBounds)
{var sEnumValue=""+aEnumValue+"";var sResultEnumValue="";var sResultEnumValueAdd="";for(var i=0;i<this.maxLen;i++)
{if(this.maxLen>sEnumValue.length+i)
{if(this.EnumPartType_==EnumPartType.Degit)
{if(this.minDigitValue<0)
sResultEnumValueAdd+=" ";else
sResultEnumValueAdd+="0";}
else
{sResultEnumValueAdd+=" ";}}
else
{if(this.EnumPartType_==EnumPartType.Degit)
{sResultEnumValue+=sEnumValue.charAt(i-(this.maxLen-sEnumValue.length));}
else
{sResultEnumValue=sEnumValue.charAt(sEnumValue.length-1-(i-(this.maxLen-sEnumValue.length)))+sResultEnumValue;}}}
if(this.EnumPartType_==EnumPartType.Degit)
{sResultEnumValue=sResultEnumValueAdd+sResultEnumValue;this.curLen=this.maxLen;}
else
{sResultEnumValue=sResultEnumValue+sResultEnumValueAdd;this.curLen=aEnumValue.length;}
return sResultEnumValue;}
this.set_CurrentValueIndex=function(aIndex){if(this.EnumPartType_==EnumPartType.Symbol){this.curValueIndex=aIndex;}else if(this.EnumPartType_==EnumPartType.Degit){if(aIndex==0){this.currentDigitValue=this.minDigitValue;}else{this.currentDigitValue=this.maxDigitValue;}}}
this.isValidValueForCurrentDegitEnum=function(value){value=value*1;if(isNaN(value))
return false;if(value!=Math.round(value))
return false;if(this.minDigitValue<=value&&value<=this.maxDigitValue)
return true;return false;}
this.set_CurrentValue=function(input,aBegIndex,aActionName,aResultObj){if(this.maxLen>this.curLen){aBegIndex=aBegIndex-(this.maxLen-this.curLen);if(aBegIndex<0)
aBegIndex=0;}
if(aActionName==undefined)
aActionName="default";if(aBegIndex==undefined){aBegIndex=0;}else if((aBegIndex-this.realBeginIndex)>=0){aBegIndex=aBegIndex-this.realBeginIndex;}else{aBegIndex=0;}
if(this.EnumPartType_==EnumPartType.Symbol){var aMaxEqualsCount=0;var aSelectedValueIndex=-1;var i=this.curValueIndex+1;var whileTag=0;var whileLen=arr.length;while(whileTag<2){if(i>=whileLen&&whileTag==0){whileTag=1;whileLen=this.curValueIndex+1;i=0;}
if(i>=whileLen&&whileTag==1){break;}
var aCurEqualsCount=0;var aCurValue=arr[i];var aCurMaxLen=aCurValue.length;for(var j=aBegIndex;j<aCurMaxLen;j++){if((j-aBegIndex)>=input.length)
break;if((aCurValue.charAt(j)).toLowerCase()==(input.charAt(j-aBegIndex)).toLowerCase()){aCurEqualsCount++;}}
if(aCurEqualsCount>aMaxEqualsCount){aMaxEqualsCount=aCurEqualsCount;aSelectedValueIndex=i;}
i++;}
if(aSelectedValueIndex!=-1){this.curValueIndex=aSelectedValueIndex;return true;}else{return false;}}else if(this.EnumPartType_==EnumPartType.Degit){var s=this.ApplyFormatToEnumValue(this.currentDigitValue);if((aBegIndex+input.length)>s.length)
return false;if(aActionName=='delete'){var aFoundValidPosForEnum=-1;for(var i=0;i<s.length;i++){if(s.charAt(i)!=' '&&s.charAt(i)!='0'&&aFoundValidPosForEnum==-1)
aFoundValidPosForEnum=i;}
if((s.charAt(aBegIndex)=='0'||s.charAt(aBegIndex)==' ')&&aActionName=='delete')
aBegIndex=aFoundValidPosForEnum==-1?0:aFoundValidPosForEnum;}
var s1=set_CharacterInString(s,input,aBegIndex);if(s1.indexOf(".")!=-1)
return false;if(this.isValidValueForCurrentDegitEnum(s1)==true){this.currentDigitValue=s1*1;return true;}else{if(this._parentTextProvider._isSmartInputMode()){if(input.length==1){if(aActionName!='delete'){for(var ii=aBegIndex;ii<s.length;ii++){var sTestVal=set_CharacterInString(s,input,ii);if(this.isValidValueForCurrentDegitEnum(sTestVal)==true){this.currentDigitValue=sTestVal*1;aResultObj.result_offset=ii-aBegIndex;return true;}}}}}}}
return false;}
this.ClearValue=function(){if(this.EnumPartType_==EnumPartType.Symbol){this.curValueIndex=this.initialValue;}else if(this.EnumPartType_==EnumPartType.Degit){this.currentDigitValue=this.initialValue;}}
this.get_CurrentValue=function(){if(this.EnumPartType_==EnumPartType.Symbol){return this.ApplyFormatToEnumValue(this.arr[this.curValueIndex],true);}else if(this.EnumPartType_==EnumPartType.Degit){return this.ApplyFormatToEnumValue(this.currentDigitValue*1);}
return"*ENUM_ERROR*";}
this.GetArrayOfAvilableValues=function(){return this.arr;}
this.doIncrement=function(aIncVal){if(aIncVal==null)
aIncVal=1;if(this.EnumPartType_==EnumPartType.Symbol){this.curValueIndex++;if(this.curValueIndex>=this.arr.length)
this.curValueIndex=0;return true;}else if(this.EnumPartType_==EnumPartType.Degit){if((this.currentDigitValue*1+aIncVal)<=this.maxDigitValue){this.currentDigitValue=this.currentDigitValue+aIncVal;return true;}else{return false;}}
return false;}
this.doDecrement=function(aIncVal){if(aIncVal==null)
aIncVal=1;if(this.EnumPartType_==EnumPartType.Symbol){this.curValueIndex--;if(this.curValueIndex<0)
this.curValueIndex=this.arr.length-1;return true;}else if(this.EnumPartType_==EnumPartType.Degit){if((this.currentDigitValue*1-aIncVal)>=this.minDigitValue){this.currentDigitValue=this.currentDigitValue-aIncVal;return true;}else{return false;}}
return false;}
this.IsIndexInRangeOfEnumPart=function(aTestIndex){if(aTestIndex>=this.beginIndex&&aTestIndex<(this.beginIndex+this.maxLen))
return true;return false;}}
function EnumPartsWorker(aParent)
{this.enumPartsCount=0;this.enumPartsCollection=new Array();this.loadEnumPart=function(s,beginIndex)
{var id=this.enumPartsCount;var aEnumPart=null;if(s.indexOf('|')!=-1)
{var arr=s.split('|');aEnumPart=new EnumPart(id,arr,EnumPartType.Symbol,beginIndex,aParent);this.enumPartsCollection.push(aEnumPart);}
else if(s.indexOf("...")!=-1)
{var arr=s.split("...");if(arr[1].indexOf("(")!=-1){var aTmpArr=arr[1].split("(");arr[1]=aTmpArr[0];aTmpArr=aTmpArr[1].split(")");aTmpArr=aTmpArr[0].split(":");aEnumPart=new EnumPart(id,arr,EnumPartType.Degit,beginIndex,aParent);this.enumPartsCollection.push(aEnumPart);}else{aEnumPart=new EnumPart(id,arr,EnumPartType.Degit,beginIndex,aParent);this.enumPartsCollection.push(aEnumPart);}}else{return null;}
this.enumPartsCount++;return aEnumPart;}
this.getEnumPartById=function(aId){for(var i=0;i<this.enumPartsCollection.length;i++){if(this.enumPartsCollection[i].id==aId)
return this.enumPartsCollection[i];}
return null;}
this.getEnumPartObjectForPosition=function(aPos){for(var i=0;i<this.enumPartsCollection.length;i++){if(this.enumPartsCollection[i].IsIndexInRangeOfEnumPart(aPos)==true)
return this.enumPartsCollection[i];}
return null;}}
function C1MaskedTextProvider()
{this.AllowPromptAsInput=false;this.IsPassword=false;this.PasswordChar="";this.ResetOnPrompt=true;this.ResetOnSpace=true;this.SkipLiterals=true;this.allowAnyCharacters=false;this.ASCII_ONLY="ASCII_ONLY";this.INCLUDE_PROMPT="INCLUDE_PROMPT";this.INCLUDE_LITERALS="INCLUDE_LITERALS";this.RESET_ON_PROMPT="RESET_ON_PROMPT";this.mask="";this.testString="";this.InvalidIndex=-1;this.HaveEnumParts=false;this.assignedCharCount=0;this.requiredCharCount=0;this.C1CharactersValidator_=null;this.EnumPartsWorker_=new EnumPartsWorker(this);this.constructor=function(mask,restrictToAscii)
{culture=new CultureInfo();PromptChar="_";this.allowAnyCharacters=false;this.HaveEnumParts=false;this.culture=culture;this.C1CharactersValidator_=new C1CharactersValidator(culture);this.initialMask=mask;this.mask=mask;this.PromptChar=PromptChar;this.Initialize();}
this.set_CultureInfo=function(aCulture){if(aCulture!=undefined){var aText=this.ToString(true,false,false);this.culture=aCulture;this.C1CharactersValidator_=new C1CharactersValidator(aCulture);this.Initialize();this.Set(aText);}}
this.get_CultureInfo=function(){return this.culture;}
this.set_PromptChar=function(value){this.PromptChar=value;if(this.allowAnyCharacters==true){return;}
for(var i=0;i<this.stringDescriptor.length;i++){var descriptor1=this.stringDescriptor[i];if(descriptor1.CharType==CharType.EditOptional||descriptor1.CharType==CharType.EditRequired){if(descriptor1.IsAssigned==false){this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,this.PromptChar,i);}}}}
this.get_HaveEnumParts=function(){return this.HaveEnumParts;}
this.ParseEnumerationParts=function(mask){if(mask==undefined)
mask="";this.EnumPartsWorker_=new EnumPartsWorker(this);var sResultMask="";var aEndTagIndex=0;var aBegTagIndex=mask.indexOf("<<",0);if(aBegTagIndex==-1)
return mask;while(aBegTagIndex!=-1)
{sResultMask+=mask.substr(0,aBegTagIndex);mask=mask.substr(aBegTagIndex);aBegTagIndex=0;aEndTagIndex=mask.indexOf(">>",0);if(aEndTagIndex!=-1)
{var s=mask.substr(2,aEndTagIndex-2);var aEnumPart=this.EnumPartsWorker_.loadEnumPart(s,sResultMask.length);if(aEnumPart!=null){this.HaveEnumParts=true;aEnumPart.positionInMask=sResultMask.length;sResultMask+=aEnumPart.get_CurrentValue();}else{sResultMask+="<"+s+">";}
mask=mask.substr(aEndTagIndex+2);}
else
{sResultMask+=mask.substr(aBegTagIndex);mask="";}
aBegTagIndex=mask.indexOf("<<",0);}
sResultMask+=mask;return sResultMask;}
this.Clone=function()
{var provider1=new MaskedTextProvider();provider1.constructor(this.Mask,this.culture,this.AsciiOnly);provider1.ResetOnPrompt=this.ResetOnPrompt;provider1.ResetOnSpace=this.ResetOnSpace;provider1.SkipLiterals=this.SkipLiterals;provider1.IncludeLiterals=this.IncludeLiterals;provider1.IncludePrompt=this.IncludePrompt;return provider1;}
this.Initialize=function(){if(this.initialMask==undefined||this.initialMask.length<=0)
{this.allowAnyCharacters=true;}else{this.allowAnyCharacters=false;}
if(this.allowAnyCharacters==true)
return;this.mask=this.ParseEnumerationParts(this.initialMask);this.testString="";this.optionalEditChars=0;this.assignedCharCount=0;this.requiredCharCount=0;this.stringDescriptor=new Array();var conversion1=CaseConversion.None;var flag1=false;var num1=0;var type1=CharType.Literal;var text1="";for(var num2=0;num2<this.mask.length;num2++)
{var aNeedCharDescriptorNow=false;var ch1=this.mask.charAt(num2);var aTestForEnumPartObject=this.EnumPartsWorker_.getEnumPartObjectForPosition(num2);if(aTestForEnumPartObject!=null){type1=CharType.Literal;aNeedCharDescriptorNow=true;}
if(flag1)
{flag1=false;aNeedCharDescriptorNow=true;}
if(aNeedCharDescriptorNow==false)
{var ch3=ch1;if(ch3<='C')
{switch(ch3)
{case'#':case'9':case'?':case'C':this.optionalEditChars++;ch1=this.PromptChar;type1=CharType.EditOptional;aNeedCharDescriptorNow=true;break;case'$':text1=this.culture.NumberFormat.CurrencySymbol;type1=CharType.Separator;aNeedCharDescriptorNow=true;break;case'%':case'-':case';':case'=':case'@':case'B':type1=CharType.Literal;aNeedCharDescriptorNow=true;break;case'&':case'0':case'A':this.requiredEditChars++;ch1=this.PromptChar;type1=CharType.EditRequired;aNeedCharDescriptorNow=true;break;case',':text1=this.culture.NumberFormat.NumberGroupSeparator;type1=CharType.Separator;aNeedCharDescriptorNow=true;break;case'.':text1=this.culture.NumberFormat.NumberDecimalSeparator;type1=CharType.Separator;aNeedCharDescriptorNow=true;break;case'/':text1=this.culture.DateTimeFormat.DateSeparator;type1=CharType.Separator;aNeedCharDescriptorNow=true;break;case':':text1=this.culture.DateTimeFormat.TimeSeparator;type1=CharType.Separator;aNeedCharDescriptorNow=true;break;case'<':conversion1=CaseConversion.ToLower;continue;case'>':conversion1=CaseConversion.ToUpper;continue;}
if(aNeedCharDescriptorNow==false){type1=CharType.Literal;aNeedCharDescriptorNow=true;}}
if(aNeedCharDescriptorNow==false){if(ch3<='\\')
{switch(ch3)
{case'L':this.requiredEditChars++;ch1=this.PromptChar;type1=CharType.EditRequired;aNeedCharDescriptorNow=true;break;case'\\':flag1=true;type1=CharType.Literal;continue;}
if(aNeedCharDescriptorNow==false){type1=CharType.Literal;aNeedCharDescriptorNow=true;}}
if(aNeedCharDescriptorNow==false){if(ch3=='a')
{this.optionalEditChars++;ch1=this.PromptChar;type1=CharType.EditOptional;aNeedCharDescriptorNow=true;}
if(aNeedCharDescriptorNow==false){if(ch3!='|')
{type1=CharType.Literal;aNeedCharDescriptorNow=true;}
if(aNeedCharDescriptorNow==false){conversion1=CaseConversion.None;continue;}}}}}
if(aNeedCharDescriptorNow==true){var descriptor1;descriptor1=new CharDescriptor(num2,type1);descriptor1.EnumPartObject=this.EnumPartsWorker_.getEnumPartObjectForPosition(num2);if(descriptor1.EnumPartObject!=null){if(descriptor1.EnumPartObject.realBeginIndex==undefined||descriptor1.EnumPartObject.realBeginIndex==-1){descriptor1.EnumPartObject.realBeginIndex=num1;}}
if(this.IsEditPosition(descriptor1))
{descriptor1.CaseConversion=conversion1;}
if(type1!=CharType.Separator)
{text1=ch1;}
for(var ii=0;ii<text1.length;ii++)
{var ch2=text1.charAt(ii);this.testString=this.testString+ch2;this.stringDescriptor.push(descriptor1);num1++;}}}
this.testString.Capacity=this.testString.length;}
this.ToString=function(ignorePasswordChar,includePrompt,includeLiterals,startPosition,length)
{if(this.allowAnyCharacters==true){if(ignorePasswordChar==false){var s="";for(var i=0;i<this.testString.length;i++){s+=this.PasswordChar;}
return s;}
return this.testString;}
if(ignorePasswordChar==undefined)
ignorePasswordChar=true;if(includePrompt==undefined)
includePrompt=this.IncludePrompt;if(includeLiterals==undefined)
includeLiterals=this.IncludeLiterals;if(startPosition==undefined)
startPosition=0;if(length==undefined)
length=this.testString.length;if(length<=0)
return"";if(startPosition<0)
startPosition=0;if(startPosition>=this.testString.length)
return"";var num1=this.testString.length-startPosition;if(length>num1)
length=num1;if((!this.IsPassword||ignorePasswordChar)&&(includePrompt&&includeLiterals))
{var aResult=this.testString.substring(startPosition,length-startPosition);return aResult;}
var builder1="";var num2=(startPosition+length)-1;for(var num5=startPosition;num5<=num2;num5++)
{var ch1=this.testString.charAt(num5);var descriptor1=this.stringDescriptor[num5];switch(descriptor1.CharType)
{case CharType.EditOptional:case CharType.EditRequired:if(!descriptor1.IsAssigned)
{break;}
if(!this.IsPassword||ignorePasswordChar)
{builder1=builder1+ch1;continue;}
builder1=builder1+this.PasswordChar;continue;case(CharType.EditRequired|CharType.EditOptional):builder1=builder1+ch1;continue;case CharType.Separator:case CharType.Literal:if(descriptor1.EnumPartObject!=null){builder1=builder1+ch1;continue;}
if(!includeLiterals)
{continue;}
builder1=builder1+ch1;continue;default:builder1=builder1+ch1;continue;}
if(includePrompt)
{builder1=builder1+ch1;continue;}
builder1=builder1+' ';continue;if(!includeLiterals)
{continue;}
builder1=builder1+ch1;continue;}
return builder1;}
this.IsEditPosition=function(charDescriptor){if(this.allowAnyCharacters==true){return true;}
if(charDescriptor.CharType!=CharType.EditRequired)
{return(charDescriptor.CharType==CharType.EditOptional);}
return true;}
this.IsEditPositionAt=function(position){if(this.allowAnyCharacters==true){return true;}
if((position<0)||(position>=this.testString.length))
{return false;}
var descriptor1=this.stringDescriptor[position];return this.IsEditPosition(descriptor1);}
this.FindNonEditPositionInRange=function(startPosition,endPosition,direction)
{var type1=trueOR(CharType.Literal,CharType.Separator);return this.FindPositionInRange(startPosition,endPosition,direction,type1);}
this.FindPositionInRange=function(startPosition,endPosition,direction,charTypeFlags)
{if(startPosition<0)
{startPosition=0;}
if(endPosition>=this.testString.length)
{endPosition=this.testString.length-1;}
if(startPosition<=endPosition)
{while(startPosition<=endPosition)
{var num1=direction?startPosition++:endPosition--;var descriptor1=this.stringDescriptor[num1];if(((descriptor1.CharType&0xFFFFFFFF)&(charTypeFlags&0xFFFFFFFF))==descriptor1.CharType)
{return num1;}}}
return-1;}
this.FindAssignedEditPositionInRange=function(startPosition,endPosition,direction)
{if(this.assignedCharCount==0)
{return-1;}
return this.FindEditPositionInRange(startPosition,endPosition,direction,2);}
this.FindEditPositionInRange=function(startPosition,endPosition,direction,assignedStatus)
{do
{var num1=this.FindEditPositionInRange2(startPosition,endPosition,direction);if(num1==-1)
{break;}
var descriptor1=this.stringDescriptor[num1];switch(assignedStatus)
{case 1:if(!descriptor1.IsAssigned)
{return num1;}
break;case 2:if(descriptor1.IsAssigned)
{return num1;}
break;default:return num1;}
if(direction)
{startPosition++;}
else
{endPosition--;}}
while(startPosition<=endPosition);return-1;}
this.FindEditPositionInRange2=function(startPosition,endPosition,direction)
{var type1=trueOR(CharType.EditRequired,CharType.EditOptional);return this.FindPositionInRange(startPosition,endPosition,direction,type1);}
this.FindAssignedEditPositionFrom=function(position,direction)
{var num1;var num2;if(this.assignedCharCount==0)
{return-1;}
if(direction)
{num1=position;num2=this.testString.length-1;}
else
{num1=0;num2=position;}
return this.FindAssignedEditPositionInRange(num1,num2,direction);}
this.ResetString=function(startPosition,endPosition)
{if(this.allowAnyCharacters==true){this.testString="";return;}
startPosition=this.FindAssignedEditPositionFrom(startPosition,true);if(startPosition!=-1)
{endPosition=this.FindAssignedEditPositionFrom(endPosition,false);while(startPosition<=endPosition)
{startPosition=this.FindAssignedEditPositionFrom(startPosition,true);this.ResetChar(startPosition);startPosition++;}}}
this.ResetChar=function(testPosition)
{var descriptor1=this.stringDescriptor[testPosition];if(this.IsEditPositionAt(testPosition)&&descriptor1.IsAssigned)
{descriptor1.IsAssigned=false;this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,this.PromptChar,testPosition);this.assignedCharCount--;if(descriptor1.CharType==CharType.EditRequired)
{this.requiredCharCount--;}}}
this.RemoveAtInt=function(startPosition,endPosition,resultHint,testOnly)
{if(this.allowAnyCharacters==true){try{this.testString=this.testString.substring(0,startPosition)+this.testString.substring(endPosition+1,this.testString.length);resultHint.testPosition=startPosition;}catch(ex){}
return;}
var hint1=new MaskedTextResultHint();if(!testOnly){if(this.handleEnumerationPart(' ',startPosition,resultHint,"delete")==true){for(var i=startPosition+1;i<=endPosition;i++){this.handleEnumerationPart(' ',i,resultHint,"delete")}
return true;}}
var ch1;var ch2;var num1=this.FindAssignedEditPositionFrom(this.testString.length-1,false);var num2=this.FindEditPositionInRange(startPosition,endPosition,true);resultHint.hint=resultHint.NoEffect;if((num2==-1)||(num2>num1))
{resultHint.testPosition=startPosition;return true;}
resultHint.testPosition=startPosition;var flag1=endPosition<num1;if(this.FindAssignedEditPositionInRange(startPosition,endPosition,true)!=-1)
{resultHint.hint=resultHint.Success;}
if(flag1)
{var num3=this.FindEditPositionFrom(endPosition+1,true);var num4=num3;startPosition=num2;var aNeedRepeat=true;while(aNeedRepeat==true){aNeedRepeat=false;ch1=this.testString.charAt(num3);var descriptor1=this.stringDescriptor[num3];if(((ch1!=this.PromptChar)||descriptor1.IsAssigned)&&!this.TestChar(ch1,num2,hint1))
{resultHint.hint=hint1.hint;resultHint.testPosition=num2;return false;}
if(num3!=num1)
{num3=this.FindEditPositionFrom(num3+1,true);num2=this.FindEditPositionFrom(num2+1,true);aNeedRepeat=true;continue;}}
if(resultHint.SideEffect>resultHint.hint)
{resultHint.hint=resultHint.SideEffect;}
if(testOnly)
{return true;}
num3=num4;num2=startPosition;var aNeedRepeat2=true;while(aNeedRepeat2==true){aNeedRepeat2=false;ch2=this.testString.charAt(num3);var descriptor2=this.stringDescriptor[num3];if((ch2==this.PromptChar)&&!descriptor2.IsAssigned)
{this.ResetChar(num2);}
else
{this.SetChar(ch2,num2);this.ResetChar(num3);}
if(num3!=num1)
{num3=this.FindEditPositionFrom(num3+1,true);num2=this.FindEditPositionFrom(num2+1,true);aNeedRepeat2=true;continue;}}
startPosition=num2+1;}
if(startPosition<=endPosition)
{this.ResetString(startPosition,endPosition);}
return true;}
this.RemoveAt=function(startPosition,endPosition,resultHint)
{if(endPosition==undefined)
endPosition=startPosition;if(resultHint==undefined)
resultHint=new MaskedTextResultHint();if(endPosition>=this.testString.length)
{resultHint.testPosition=endPosition;resultHint.hint=MaskedTextResultHint.PositionOutOfRange;return false;}
if((startPosition>=0)&&(startPosition<=endPosition))
{var aResult=this.RemoveAtInt(startPosition,endPosition,resultHint,false);return aResult;}
resultHint.testPosition=startPosition;resultHint.hint=MaskedTextResultHint.PositionOutOfRange;return false;}
this.Clear=function(resultHint)
{if(this.allowAnyCharacters==true){this.testString="";resultHint.hint=resultHint.Success;return;}
if(this.assignedCharCount==0)
{resultHint.hint=resultHint.NoEffect;}
else
{resultHint.hint=resultHint.Success;for(var num1=0;num1<this.testString.length;num1++)
{this.ResetChar(num1);}}}
this.Set=function(input,resultHint)
{if(resultHint==undefined){resultHint=new MaskedTextResultHint();}
if(input==undefined)
{throw new"SetFromPos: input parameter is null or undefined.";}
resultHint.hint=resultHint.Unknown;resultHint.testPosition=0;if(input.length==0)
{this.Clear(resultHint);return true;}
if(this.allowAnyCharacters==true){this.testString=input;return true;}
if(this.HaveEnumParts==true){this.Clear(resultHint);resultHint.testPosition=0;return this.InsertAt(input,0,resultHint);}
if(!this.TestSetString(input,resultHint.testPosition,resultHint))
{return false;}
var num1=this.FindAssignedEditPositionFrom(resultHint.testPosition+1,true);if(num1!=-1)
{this.ResetString(num1,this.testString.length-1);}
return true;}
this.GetAdjustedPosition=function(position){if(this.allowAnyCharacters==true){if(position>=this.testString.length)
position=this.testString.length-1;}else{if(position>=this.stringDescriptor.length)
position=position-1;}
if(position<0)
position=0;return position;}
this.Get_EnumPartObjectForPosition=function(position){if(this.allowAnyCharacters==true){return null;}
position=this.GetAdjustedPosition(position);var aTestEnumDescriptor=this.stringDescriptor[position];if(aTestEnumDescriptor){if(aTestEnumDescriptor.EnumPartObject!=null){return aTestEnumDescriptor.EnumPartObject;}}
return null;}
this.doSetEnumerationIndex=function(aIndex,aEnumObject){var aBoolValue=aEnumObject.set_CurrentValueIndex(aIndex);var aValue=aEnumObject.get_CurrentValue();for(var i=0;i<aEnumObject.maxLen;i++){var aChar=aValue.charAt(i);this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,aChar,aEnumObject.realBeginIndex+i);}
return aBoolValue;}
this.doClearEnumerationPartValue=function(position){position=this.GetAdjustedPosition(position);var aTestEnumDescriptor=this.stringDescriptor[position];if(aTestEnumDescriptor.EnumPartObject!=null){if(aTestEnumDescriptor.EnumPartObject.EnumPartType_==EnumPartType.Degit){aTestEnumDescriptor.EnumPartObject.set_CurrentValue("0",position,"",null);}else{aTestEnumDescriptor.EnumPartObject.ClearValue();}
var aValue=aTestEnumDescriptor.EnumPartObject.get_CurrentValue();for(var i=0;i<aTestEnumDescriptor.EnumPartObject.maxLen;i++){var aChar=aValue.charAt(i);this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,aChar,aTestEnumDescriptor.EnumPartObject.realBeginIndex+i);}
return true;}
return false;}
this.doIncrementEnumerationPart=function(position,resultHint,aIncVal){if(this.allowAnyCharacters==true){return false;}
position=this.GetAdjustedPosition(position);var aTestEnumDescriptor=this.stringDescriptor[position];if(aTestEnumDescriptor!=undefined){if(aTestEnumDescriptor.EnumPartObject!=undefined){aTestEnumDescriptor.EnumPartObject.doIncrement(aIncVal);var aValue=aTestEnumDescriptor.EnumPartObject.get_CurrentValue();for(var i=0;i<aTestEnumDescriptor.EnumPartObject.maxLen;i++){var aChar=aValue.charAt(i);this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,aChar,aTestEnumDescriptor.EnumPartObject.realBeginIndex+i);}
return true;}}
return false;}
this.doDecrementEnumerationPart=function(position,resultHint,aIncVal){if(this.allowAnyCharacters==true){return false;}
position=this.GetAdjustedPosition(position);var aTestEnumDescriptor=this.stringDescriptor[position];if(aTestEnumDescriptor!=undefined){if(aTestEnumDescriptor.EnumPartObject!=undefined){aTestEnumDescriptor.EnumPartObject.doDecrement(aIncVal);var aValue=aTestEnumDescriptor.EnumPartObject.get_CurrentValue();for(var i=0;i<aTestEnumDescriptor.EnumPartObject.maxLen;i++){var aChar=aValue.charAt(i);this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,aChar,aTestEnumDescriptor.EnumPartObject.realBeginIndex+i);}
return true;}}
return false;}
this.findNextEnumPartPosition=function(aPos){while(true){if(aPos==-1||aPos>this.stringDescriptor.length-1)
return-1;var aTestEnumDescriptor=this.stringDescriptor[aPos];if(aTestEnumDescriptor==undefined)
return-1;if(aTestEnumDescriptor.EnumPartObject!=null){return aPos;}
aPos++}}
this.handleEnumerationPart=function(input,position,resultHint,aActionName){try{if(position==-1)
return false;var aTestEnumDescriptor=this.stringDescriptor[position];if(aTestEnumDescriptor==undefined){return false;}
var aNextInputValue="";var aEnumPartLen=-1;var aBoolResult=false;if(aTestEnumDescriptor.EnumPartObject!=null){if(aActionName!=undefined&&aActionName=="delete"){this.doClearEnumerationPartValue(position);resultHint.testPosition=position;return true;}else{aEnumPartLen=aTestEnumDescriptor.EnumPartObject.maxLen;if(input.length>aEnumPartLen){aNextInputValue=input.slice(aEnumPartLen);input=input.substr(0,aEnumPartLen);}
var aResultObj={"real_val":input,"pos":position,"result_offset":0};if(aTestEnumDescriptor.EnumPartObject.set_CurrentValue(input,position,aActionName,aResultObj)==true){resultHint.testPosition=position+input.length-1+aResultObj.result_offset;aEnumPartLen=aTestEnumDescriptor.EnumPartObject.maxLen;aBoolResult=true;}else{resultHint.testPosition=position-1;aBoolResult=false;}
var aValue=aTestEnumDescriptor.EnumPartObject.get_CurrentValue();for(var i=0;i<aTestEnumDescriptor.EnumPartObject.maxLen;i++){var aChar=aValue.charAt(i);this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,aChar,aTestEnumDescriptor.EnumPartObject.realBeginIndex+i);}}}
if(aBoolResult==true&&aEnumPartLen!=-1&&aNextInputValue!=""){var aPrevPos=position+aEnumPartLen;var aNewPos=this.findNextEnumPartPosition(aPrevPos);if(aNewPos>aPrevPos){try{var aNextInputValueTest=aNextInputValue;var aDiff=aNewPos-aPrevPos;var i=0;while(i<aDiff){var ch1=this.testString.charAt(aPrevPos+i);var ch2=aNextInputValue.charAt(0+i);if(ch1==ch2){aNextInputValueTest=aNextInputValue.slice(1);}
i++;}
aNextInputValue=aNextInputValueTest;}catch(ex){}}
this.handleEnumerationPart(aNextInputValue,aNewPos,resultHint,aActionName);return true;}
return aBoolResult;}catch(ex){return false;}}
this.InsertAtInt=function(input,position,resultHint,testOnly)
{if(input.length==0)
{resultHint.testPosition=position;resultHint.hint=resultHint.NoEffect;return true;}
if(!testOnly){if(this.handleEnumerationPart(input,position,resultHint)==true){return true;}}
if(!this.TestString(input,position,resultHint))
{return false;}
var num1=this.FindEditPositionFrom(position,true);var flag1=this.FindAssignedEditPositionInRange(num1,resultHint.testPosition,true)!=-1;var num2=this.FindAssignedEditPositionFrom(this.testString.length-1,false);if(flag1&&(resultHint.testPosition==(this.testString.length-1)))
{resultHint.hint=resultHint.UnavailableEditPosition;resultHint.testPosition=this.testString.length;return false;}
var num3=this.FindEditPositionFrom(resultHint.testPosition+1,true);if(!flag1)
{}else{var hint1=new MaskedTextResultHint();hint1.hint=hint1.Unknown;var aNeedRepeat=true;while(aNeedRepeat==true){aNeedRepeat=false;if(num3==-1)
{resultHint.hint=resultHint.UnavailableEditPosition;resultHint.testPosition=this.testString.length;return false;}
var descriptor1=this.stringDescriptor[num1];if(descriptor1.IsAssigned&&!this.TestChar(this.testString.charAt(num1),num3,hint1))
{resultHint.hint=hint1.hint;resultHint.testPosition=num3;return false;}
if(num1!=num2)
{num1=this.FindEditPositionFrom(num1+1,true);num3=this.FindEditPositionFrom(num3+1,true);aNeedRepeat=true;continue;}}
if(hint1.hint>resultHint.hint)
{resultHint.hint=hint1.hint;}}
if(!testOnly)
{if(flag1)
{while(num1>=position)
{var descriptor2=this.stringDescriptor[num1];if(descriptor2.IsAssigned)
{this.SetChar(this.testString.charAt(num1),num3);}
else
{this.ResetChar(num3);}
num3=this.FindEditPositionFrom(num3-1,false);num1=this.FindEditPositionFrom(num1-1,false);}}
this.SetString(input,position);}
return true;}
this.InsertAt=function(input,position,resultHint)
{if(resultHint==undefined){resultHint=new MaskedTextResultHint();}
if(input==undefined)
{throw new ArgumentNullException("InsertAt: input");}
if(this.allowAnyCharacters==true){this.testString=this.testString.substring(0,position)+input+this.testString.substring(position,this.testString.length);resultHint.testPosition=position+input.length-1;return true;}
if((position>=0)&&(position<this.testString.length))
{var aResult=this.InsertAtInt(input,position,resultHint,false);return aResult;}
resultHint.testPosition=position;resultHint.hint=resultHint.PositionOutOfRange;return false;}
this.IsLiteralPosition=function(charDescriptor)
{if(charDescriptor==undefined)
return false;if(charDescriptor.CharType!=CharType.Literal)
{return(charDescriptor.CharType==CharType.Separator);}
return true;}
this.TestEscapeChar=function(input,position,charDex)
{if(position<0)
position=0;if(charDex==undefined)
charDex=this.stringDescriptor[position];if(this.IsLiteralPosition(charDex))
{if(this.SkipLiterals)
{return(input==this.testString.charAt(position));}
return false;}
if((!this.ResetOnPrompt||(input!=this.PromptChar))&&(!this.ResetOnSpace||(input!=' ')))
{return false;}
return true;}
this.FindEditPositionFrom=function(position,direction)
{var num1;var num2;if(direction)
{num1=position;num2=this.testString.length-1;}
else
{num1=0;num2=position;}
return this.FindEditPositionInRange(num1,num2,direction);}
this.TestChar=function(input,position,resultHint)
{if(!this.C1CharactersValidator_.IsPrintableChar(input))
{resultHint.hint=resultHint.InvalidInput;return false;}
var descriptor1=this.stringDescriptor[position];if(descriptor1==undefined)
return false;if(this.IsLiteralPosition(descriptor1))
{if(this.SkipLiterals&&(input==this.testString.charAt(position)))
{resultHint.hint=resultHint.CharacterEscaped;return true;}
resultHint.hint=resultHint.NonEditPosition;return false;}
if(input==this.PromptChar)
{if(this.ResetOnPrompt)
{if(this.IsEditPosition(descriptor1)&&descriptor1.IsAssigned)
{resultHint.hint=resultHint.SideEffect;}
else
{resultHint.hint=resultHint.CharacterEscaped;}
return true;}
if(!this.AllowPromptAsInput)
{resultHint.hint=resultHint.PromptCharNotAllowed;return false;}}
if((input==' ')&&this.ResetOnSpace)
{if(this.IsEditPosition(descriptor1)&&descriptor1.IsAssigned)
{resultHint.hint=resultHint.SideEffect;}
else
{resultHint.hint=resultHint.CharacterEscaped;}
return true;}
switch(this.mask.charAt(descriptor1.MaskPosition))
{case'L':if(!this.C1CharactersValidator_.IsLetter(input))
{resultHint.hint=resultHint.LetterExpected;return false;}
if(!this.C1CharactersValidator_.IsAsciiLetter(input)&&this.AsciiOnly)
{resultHint.hint=resultHint.AsciiCharacterExpected;return false;}
break;case'a':if(!this.C1CharactersValidator_.IsAlphanumeric(input)&&(input!=' '))
{resultHint.hint=resultHint.AlphanumericCharacterExpected;return false;}
if(!this.C1CharactersValidator_.IsAciiAlphanumeric(input)&&this.AsciiOnly)
{resultHint.hint=resultHint.AsciiCharacterExpected;return false;}
break;case'?':if(!this.C1CharactersValidator_.IsLetter(input)&&(input!=' '))
{resultHint.hint=resultHint.LetterExpected;return false;}
if(this.C1CharactersValidator_.IsAsciiLetter(input)||!this.AsciiOnly)
{break;}
resultHint.hint=resultHint.AsciiCharacterExpected;return false;case'A':if(!this.C1CharactersValidator_.IsAlphanumeric(input))
{resultHint.hint=resultHint.AlphanumericCharacterExpected;return false;}
if(this.C1CharactersValidator_.IsAciiAlphanumeric(input)||!this.AsciiOnly)
{break;}
resultHint.hint=resultHint.AsciiCharacterExpected;return false;case'C':if((!this.C1CharactersValidator_.IsAscii(input)&&this.AsciiOnly)&&(input!=' '))
{resultHint.hint=resultHint.AsciiCharacterExpected;return false;}
break;case'9':if(!this.C1CharactersValidator_.IsDigit(input)&&(input!=' '))
{resultHint.hint=resultHint.DigitExpected;return false;}
break;case'#':if((!this.C1CharactersValidator_.IsDigit(input)&&(input!='-'))&&((input!='+')&&(input!=' ')))
{resultHint.hint=resultHint.DigitExpected;return false;}
break;case'&':if(!this.C1CharactersValidator_.IsAscii(input)&&this.AsciiOnly)
{resultHint.hint=resultHint.AsciiCharacterExpected;return false;}
break;case'0':if(!this.C1CharactersValidator_.IsDigit(input))
{resultHint.hint=resultHint.DigitExpected;return false;}
break;}
if((input==this.testString.charAt(position))&&descriptor1.IsAssigned)
{resultHint.hint=resultHint.NoEffect;}
else
{resultHint.hint=resultHint.Success;}
return true;}
this.TestString=function(input,position,resultHint)
{resultHint.hint=resultHint.Unknown;resultHint.testPosition=position;if(input.length!=0)
{if(this.handleEnumerationPart(input,position,resultHint)==true){return true;}
var hint1=new MaskedTextResultHint();hint1.testPosition=resultHint.testPosition;hint1.hint=resultHint.hint;for(var ii=0;ii<input.length;ii++)
{var ch1=input.charAt(ii);if(resultHint.testPosition>=this.testString.length)
{resultHint.hint=resultHint.UnavailableEditPosition;return false;}
if(!this.TestEscapeChar(ch1,resultHint.testPosition))
{resultHint.testPosition=this.FindEditPositionFrom(resultHint.testPosition,true);if(resultHint.testPosition==-1)
{resultHint.testPosition=this.testString.length;resultHint.hint=resultHint.UnavailableEditPosition;return false;}}
if(!this.TestChar(ch1,resultHint.testPosition,hint1))
{resultHint.hint=hint1.hint;return false;}
if(hint1.hint>resultHint.hint)
{resultHint.hint=hint1.hint;}
resultHint.testPosition+=1;}
resultHint.testPosition-=1;}
return true;}
this.SetChar=function(input,position,charDescriptor)
{if(position<0)
position=0;if(charDescriptor==undefined){charDescriptor=this.stringDescriptor[position];}
var local1=this.stringDescriptor[position];if(this.TestEscapeChar(input,position,charDescriptor))
{this.ResetChar(position);}
else
{if(this.C1CharactersValidator_.IsLetter(input))
{if(this.C1CharactersValidator_.IsUpper(input))
{if(charDescriptor.CaseConversion==CaseConversion.ToLower)
{input=this.culture.TextInfo.ToLower(input);}}
else if(charDescriptor.CaseConversion==CaseConversion.ToUpper)
{input=this.culture.TextInfo.ToUpper(input);}}
this.testString=this.C1CharactersValidator_.setCharcterInString(this.testString,input,position);if(!charDescriptor.IsAssigned)
{charDescriptor.IsAssigned=true;this.assignedCharCount++;if(charDescriptor.CharType==CharType.EditRequired)
{this.requiredCharCount++;}}}}
this.SetString=function(input,testPosition){for(var i=0;i<input.length;i++)
{var ch1=input.charAt(i);if(!this.TestEscapeChar(ch1,testPosition))
{testPosition=this.FindEditPositionFrom(testPosition,true);}
this.SetChar(ch1,testPosition);testPosition++;}}
this.TestSetString=function(input,position,resultHint)
{if(this.TestString(input,position,resultHint))
{this.SetString(input,position);return true;}
return false;}
this.get_PostDataString=function(){return"Text|="+c__escape(this.ToString(true,false,false));}
this._isSmartInputMode=function(){if(this._parentMaskEdit!=null){return this._parentMaskEdit.get_smartInputMode();}
return true;}}