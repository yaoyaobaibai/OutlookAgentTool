
var C1NumericControlType=new Object();C1NumericControlType.Numeric=0;C1NumericControlType.Percent=1;C1NumericControlType.Currency=2;var C1DecimalDegitsEnum=new Object();C1DecimalDegitsEnum.Default=-2;C1DecimalDegitsEnum.AsIs=-1;C1DecimalDegitsEnum.Zero=0;C1DecimalDegitsEnum.One=1;C1DecimalDegitsEnum.Two=2;C1DecimalDegitsEnum.Three=3;C1DecimalDegitsEnum.Four=4;C1DecimalDegitsEnum.Five=5;C1DecimalDegitsEnum.Six=6;C1DecimalDegitsEnum.Seven=7;C1DecimalDegitsEnum.Eight=8;function C1NumericToStringFormat(aCulture,aC1NumericControlType,aDegitsPlaces,useThousandsSeparator){var culture=aCulture;var type=aC1NumericControlType;var degitsPlaces=aDegitsPlaces;this._currentExpectedValueAsText="0";this.currentText="0";this.GroupSeparator=" ";this.deFormatValue=function(sValue)
{var aDegitsPlaces=degitsPlaces;var doubleResult=NaN;var isNegative=false;var aNegIndex=sValue.indexOf("-");if(aNegIndex==-1)
aNegIndex=sValue.indexOf("(");if(aNegIndex!=-1)
isNegative=true;sValue=sValue.replace("(","");sValue=sValue.replace(")","");sValue=sValue.replace("-","");sValue=sValue.replace(culture.NumberFormat.PercentSymbol,"");sValue=sValue.replace(culture.NumberFormat.CurrencySymbol,"");var sGroupSeparator=culture.NumberFormat.NumberGroupSeparator;var sDecimalSeparator=culture.NumberFormat.NumberDecimalSeparator;switch(type)
{case C1NumericControlType.Percent:sGroupSeparator=culture.NumberFormat.PercentGroupSeparator;sDecimalSeparator=culture.NumberFormat.PercentDecimalSeparator;break;case C1NumericControlType.Currency:sGroupSeparator=culture.NumberFormat.CurrencyGroupSeparator;sDecimalSeparator=culture.NumberFormat.CurrencyDecimalSeparator;break;}
this.GroupSeparator=sGroupSeparator;var r=new RegExp("["+sGroupSeparator+"]","g");sValue=sValue.replace(r,"");r=new RegExp("["+sDecimalSeparator+"]","g");sValue=sValue.replace(r,".");r=new RegExp("[ ]","g");sValue=sValue.replace(r,"");try
{var prev=sValue;var reg=/([\d\.]+)/;var arr=reg.exec(sValue);if(arr!=null)
sValue=arr[0];if(isNegative)
sValue="-"+sValue;this._currentExpectedValueAsText=sValue;this.currentText=this.formatValue(sValue);}
catch(Exception)
{}}
this.getFormattedValue=function(){return this.formatValue(this._currentExpectedValueAsText);}
this.getJSFloatValue=function(){try{if(this._currentExpectedValueAsText=="")
return 0;return parseFloat(this._currentExpectedValueAsText);}catch(ex){return NaN;}}
this.Clear=function(){this._currentExpectedValueAsText="0";}
this.setValueFromJSFloat=function(aFloatValue){try{this._currentExpectedValueAsText=aFloatValue;this.formatValue(aFloatValue);return true;}catch(e){return false;}}
this.IsZero=function(){try{var aTest=this._currentExpectedValueAsText.replace("-","");aTest=aTest.replace("(","");aTest=aTest.replace(")","");if(aTest.length==0)
aTest="0";var dbl=parseFloat(aTest);if(dbl!=NaN&&dbl==0)
return true;}catch(ex){}
return false;}
this.SetPositiveSign=function(){this._currentExpectedValueAsText=this._currentExpectedValueAsText.replace("-","");this._currentExpectedValueAsText=this._currentExpectedValueAsText.replace("(","");this._currentExpectedValueAsText=this._currentExpectedValueAsText.replace(")","");}
this.InvertSign=function(){var aValueIsNegative=false;if(this._currentExpectedValueAsText.indexOf("-")!=-1||this._currentExpectedValueAsText.indexOf("(")!=-1)
aValueIsNegative=true;if(aValueIsNegative==true)
this.SetPositiveSign();else
this._currentExpectedValueAsText=this._currentExpectedValueAsText.length==0?"0":"-"+this._currentExpectedValueAsText;if(this.IsZero()){this._currentExpectedValueAsText="0";}
this.formatValue(this._currentExpectedValueAsText);}
this.Increment=function(aIncVal){if(aIncVal==null)
aIncVal=1;try{var arr=this._currentExpectedValueAsText.split(".");this._currentExpectedValueAsText=(arr[0]*1+aIncVal)+""+(arr.length>1?("."+arr[1]):"");}catch(ex){}}
this.Decrement=function(aIncVal){if(aIncVal==null)
aIncVal=1;try{var arr=this._currentExpectedValueAsText.split(".");this._currentExpectedValueAsText=(arr[0]*1-aIncVal)+""+(arr.length>1?("."+arr[1]):"");}catch(ex){}}
this.CheckDegitsLimits=function(aDegitsCount){try{var arr=this._currentExpectedValueAsText.split(".");var s="";if(arr.length>1){s=arr[1];}
var d="";for(var i=0;i<aDegitsCount;i++){var ch="0";if(s.length>i)
ch=s.charAt(i);d=d+ch;}
if(d.length>0){this._currentExpectedValueAsText=arr[0]+"."+d;}else{this._currentExpectedValueAsText=arr[0];}}catch(ex){}}
this.CheckMinValue=function(aValue,aCheckAndRepair,aCheckIsLessOrEqMin){if(aCheckIsLessOrEqMin==undefined)
aCheckIsLessOrEqMin=false;var aResult=true;try{var arr=this._currentExpectedValueAsText.split(".");var s1=parseFloat((arr[0]==""||arr[0]=="-")?"0":arr[0]);var s2=0;if(arr.length>1&&parseFloat(arr[1])>0){s2=parseFloat("1."+arr[1]);}
if(s1<0||arr[0]=="-")
s2=s2*-1;aValue=""+aValue+"";arr=aValue.split(".");var sv1=parseFloat(arr[0]);var sv2=0;if(arr.length>1&&parseFloat(arr[1])>0){sv2=parseFloat("1."+arr[1]);}
if(s1>sv1){return true;}
if(s1<sv1||(aCheckIsLessOrEqMin==true&&s1==sv1&&s2<=sv2)){aResult=false;}else if(s1==sv1&&s1<0&&s2>sv2){aResult=false;}else if(s1==sv1&&s1>=0&&s2<sv2){aResult=false;}
if(aResult==false&&aCheckAndRepair==true)
this._currentExpectedValueAsText=""+aValue+"";}catch(ex){}
return aResult;}
this.CheckMaxValue=function(aValue,aCheckAndRepair){var aResult=true;try{var arr=this._currentExpectedValueAsText.split(".");var s1=parseFloat((arr[0]==""||arr[0]=="-")?"0":arr[0]);var s2=0;if(arr.length>1&&parseFloat(arr[1])>0){s2=parseFloat("1."+arr[1]);}
if(s1<0||arr[0]=="-")
s2=s2*-1;aValue=""+aValue+"";arr=aValue.split(".");var sv1=parseFloat(arr[0]);var sv2=0;if(arr.length>1&&parseFloat(arr[1])>0){sv2=parseFloat("1."+arr[1]);}
if(s1<sv1){return true;}
if(s1>sv1){aResult=false;}
if(s1==sv1&&s1>=0&&s2>sv2){aResult=false;}
if(s1==sv1&&s1<0&&s2<sv2){aResult=false;}
if(aResult==false&&aCheckAndRepair==true)
this._currentExpectedValueAsText=""+aValue+"";}catch(ex){}
return aResult;}
this.formatValue=function(value)
{value=""+value+"";var aDegitsPlaces=degitsPlaces;var aGroupSeparator=" ";var aDecimalSeparator=".";var aDecimalDegitsCount=2;var aValueIsNegative=false;if(value.indexOf("-")!=-1||value.indexOf("(")!=-1){if(!this.IsZero()){aValueIsNegative=true;}}
var aGroupSizes=new Array(3);aGroupSizes.push(3);var sFormatPattern="n";switch(type){case C1NumericControlType.Numeric:if(aValueIsNegative==true)
sFormatPattern=this.getNumberNegativePattern(culture.NumberFormat.NumberNegativePattern);else
sFormatPattern="n";aGroupSeparator=culture.NumberFormat.NumberGroupSeparator;aDecimalSeparator=culture.NumberFormat.NumberDecimalSeparator;aDecimalDegitsCount=culture.NumberFormat.NumberDecimalDigits;aGroupSizes=culture.NumberFormat.NumberGroupSizes;break;case C1NumericControlType.Percent:if(aValueIsNegative==true)
sFormatPattern=this.getPercentNegativePattern(culture.NumberFormat.PercentNegativePattern);else
sFormatPattern=this.getPercentPositivePattern(culture.NumberFormat.PercentPositivePattern);aGroupSeparator=culture.NumberFormat.PercentGroupSeparator;aDecimalSeparator=culture.NumberFormat.PercentDecimalSeparator;aDecimalDegitsCount=culture.NumberFormat.PercentDecimalDigits;aGroupSizes=culture.NumberFormat.PercentGroupSizes;break;case C1NumericControlType.Currency:if(aValueIsNegative==true)
sFormatPattern=this.getCurrencyNegativePattern(culture.NumberFormat.CurrencyNegativePattern);else
sFormatPattern=this.getCurrencyPositivePattern(culture.NumberFormat.CurrencyPositivePattern);aGroupSeparator=culture.NumberFormat.CurrencyGroupSeparator;aDecimalSeparator=culture.NumberFormat.CurrencyDecimalSeparator;aDecimalDegitsCount=culture.NumberFormat.CurrencyDecimalDigits;aGroupSizes=culture.NumberFormat.CurrencyGroupSizes;break;default:break;}
if(aDegitsPlaces!=C1DecimalDegitsEnum.Default)
{if(aDegitsPlaces==C1DecimalDegitsEnum.AsIs)
{aDecimalDegitsCount=-1;}
else
{aDecimalDegitsCount=aDegitsPlaces;}}
if(useThousandsSeparator==false){aGroupSizes=new Array();aGroupSizes.push(0);}
value=value.replace(/^[0]+/,"");var sDegitsString=this.formatDegits(value,aGroupSeparator,aDecimalSeparator,aDecimalDegitsCount,aGroupSizes);sDegitsString=sDegitsString.replace(/^[0]+/,"");if(sDegitsString.indexOf(aDecimalSeparator)==0){sDegitsString="0"+sDegitsString;}
if(sDegitsString=="")
sDegitsString="0";if(aValueIsNegative){this._currentExpectedValueAsText=value;}else{this._currentExpectedValueAsText=value;}
this.currentText=this.applyFormatPattern(sFormatPattern,sDegitsString,culture.NumberFormat.PercentSymbol,culture.NumberFormat.CurrencySymbol);return this.currentText;}
this.applyFormatPattern=function(sFormatPattern,sDegitsString,aPercentSymbol,aCurrencySymbol)
{var sResult=sFormatPattern;var r=new RegExp("[n]","g");sResult=sResult.replace(r,sDegitsString);r=new RegExp("[%]","g");sResult=sResult.replace(r,aPercentSymbol);r=new RegExp("[$]","g");sResult=sResult.replace(r,aCurrencySymbol);return sResult;}
this.formatDegits=function(value,aGroupSeparator,aDecimalSeparator,aDecimalDegitsCount,aGroupSizes)
{var sAbsValue=""+value+"";sAbsValue=sAbsValue.replace("-","");sAbsValue=sAbsValue.replace("(","");sAbsValue=sAbsValue.replace(")","");var aDecIndx=sAbsValue.indexOf(aDecimalSeparator);if(aDecIndx==-1)
{aDecIndx=sAbsValue.indexOf(".");}
if(aDecIndx==-1)
{aDecIndx=sAbsValue.indexOf(",");}
if(aDecIndx==-1)
{aDecIndx=sAbsValue.length;}
var sResult="";var aGroupSizesIndx=0;var aGroupCount=0;for(var i=sAbsValue.length-1;i>=0;i--)
{var ch=sAbsValue.charAt(i);if(i<aDecIndx)
{sResult=ch+sResult;aGroupCount++;if(aGroupCount==aGroupSizes[aGroupSizesIndx]*1&&aGroupSizes[aGroupSizesIndx]*1!=0&&i!=0)
{sResult=aGroupSeparator+sResult;aGroupCount=0;if(aGroupSizes.length-1>aGroupSizesIndx)
aGroupSizesIndx++;}}}
if(aDecimalDegitsCount>0)
{sResult=sResult+aDecimalSeparator;for(var i=0;i<aDecimalDegitsCount;i++)
{var ch='0';if(i+aDecIndx+1<sAbsValue.length)
{ch=sAbsValue.charAt(i+aDecIndx+1);}
sResult=sResult+ch;}}
if(aDecimalDegitsCount==-1)
{if(aDecIndx<sAbsValue.length-1)
{sResult=sResult+aDecimalSeparator;sResult=sResult+sAbsValue.substring(aDecIndx+1);}}
return sResult;}
this.getCurrencyPositivePattern=function(p){var sResult="$n";switch(p)
{case 0:sResult="$n";break;case 1:sResult="n$";break;case 2:sResult="$ n";break;case 3:sResult="n $";break;}
return sResult;}
this.getCurrencyNegativePattern=function(p)
{var sResult="$-n";switch(p)
{case 0:sResult="($n)";break;case 1:sResult="-$n";break;case 2:sResult="$-n";break;case 3:sResult="$n-";break;case 4:sResult="(n$)";break;case 5:sResult="-n$";break;case 6:sResult="n-$";break;case 7:sResult="n$-";break;case 8:sResult="-n $";break;case 9:sResult="-$ n";break;case 10:sResult="n $-";break;case 11:sResult="$ n-";break;case 12:sResult="$ -n";break;case 13:sResult="n- $";break;case 14:sResult="($ n)";break;case 15:sResult="(n $)";break;}
return sResult;}
this.getPercentPositivePattern=function(p)
{var sResult="n%";switch(p)
{case 0:sResult="n %";break;case 1:sResult="n%";break;case 2:sResult="%n";break;case 3:sResult="% n";break;}
return sResult;}
this.getPercentNegativePattern=function(p)
{var sResult="-n%";switch(p)
{case 0:sResult="-n %";break;case 1:sResult="-n%";break;case 2:sResult="-%n";break;case 3:sResult="%-n";break;case 4:sResult="%n-";break;case 5:sResult="n-%";break;case 6:sResult="n%-";break;case 7:sResult="-%n";break;case 8:sResult="n %-";break;case 9:sResult="% n-";break;case 10:sResult="% -n";break;case 11:sResult="n- %";break;}
return sResult;}
this.getNumberNegativePattern=function(p)
{var sResult="-n";switch(p)
{case 0:sResult="(n)";break;case 1:sResult="-n";break;case 2:sResult="- n";break;case 3:sResult="n-";break;case 4:sResult="n -";break;}
return sResult;}}
function C1WebNumericEditTextProvider(aInitialValue,aMinValue,aMaxValue,aDecimalDegitsPlaces,aCulture,aNumericType,aUseThousandsSeparator){var toBool=function(value){value=""+value+"";if(value=="1"||value.toLowerCase()=="true"||value.toLowerCase()=="yes")
return true;return false;}
try{aInitialValue=aInitialValue.replace(',','.');aMinValue=aMinValue.replace(',','.');aMaxValue=aMaxValue.replace(',','.');}catch(ex){}
var pThis=this;var minValue=parseFloat(aMinValue);var minValueBool=true;var maxValue=parseFloat(aMaxValue);var maxValueBool=true;var culture=aCulture;var numericType=aNumericType;var decimalDegitsPlaces=aDecimalDegitsPlaces;var useThousandsSeparator=toBool(aUseThousandsSeparator);var C1NumericToStringFormat_=new C1NumericToStringFormat(culture,numericType,decimalDegitsPlaces,useThousandsSeparator);C1NumericToStringFormat_.setValueFromJSFloat(aInitialValue);if(isNaN(minValue))
minValueBool=false;if(isNaN(maxValue))
maxValueBool=false;var _NumberGroupSeparator=culture.NumberFormat.NumberGroupSeparator;var _NumberDecimalSeparator=culture.NumberFormat.NumberDecimalSeparator;_NumberGroupSeparator="";this.Initialize=function(){}
this.ToString=function(ignorePasswordChar,includePrompt,includeLiterals,startPosition,length){if(includePrompt==false&&pThis._parentMaskEdit._showNullText==true){if(pThis.isValueNull())
return pThis._parentMaskEdit._nullText;}
return C1NumericToStringFormat_.getFormattedValue();}
this.Set=function(input,resultHint){this.Clear();this.InsertAt(input,0,resultHint);}
this.get_HaveEnumParts=function(){return false;}
this.Clear=function(){C1NumericToStringFormat_.Clear();}
this.checkAndRepairBounds=function(aCheckAndRepair,aCheckIsLessOrEqMin){var aResult=true;if(aCheckAndRepair==undefined)
aCheckAndRepair=false;if(aCheckIsLessOrEqMin!=undefined&&aCheckIsLessOrEqMin==true){return C1NumericToStringFormat_.CheckMinValue(minValue,false,true);}
if(minValueBool){if(!C1NumericToStringFormat_.CheckMinValue(minValue,aCheckAndRepair))
aResult=false;}
if(maxValueBool){if(!C1NumericToStringFormat_.CheckMaxValue(maxValue,aCheckAndRepair))
aResult=false;}
if(decimalDegitsPlaces>=0){C1NumericToStringFormat_.CheckDegitsLimits(decimalDegitsPlaces)}
return aResult;}
var countSubstring=function(aText,aSubString){var aCount=0;var aPos=aText.indexOf(aSubString);while(aPos!=-1){aCount++;aPos=aText.indexOf(aSubString,aPos+1);}
return aCount;}
this.IsDigit=function(c)
{if(c>='0')
{return(c<='9');}
return false;}
this.getAdjustedPositionFromLeft=function(position){var currentText=C1NumericToStringFormat_.currentText;for(var i=0;i<currentText.length;i++){var ch=currentText.charAt(i);if(!this.IsDigit(ch)&&(ch!=','&&ch!='.')||ch=='0'){if(C1NumericToStringFormat_.IsZero()){if(position<i)
position++;}else{if(position<=i)
position++;}}else{break;}}
return position;}
this.InsertAt=function(input,position,resultHint){if(input==_NumberDecimalSeparator)
input=".";if(resultHint==undefined)
resultHint=new MaskedTextResultHint();if(input.length==1){if(input=='+'){C1NumericToStringFormat_.SetPositiveSign();this.checkAndRepairBounds();return true;}
if(input=='-'||input==')'||input=='('){C1NumericToStringFormat_.InvertSign();this.checkAndRepairBounds();return true;}
if(!this.IsDigit(input)){if(input!=','&&input!='.'&&input!=')'&&input!='+'&&input!='-'&&input!='('&&input!=_NumberDecimalSeparator){if(numericType==C1NumericControlType.Percent&&input==culture.NumberFormat.PercentSymbol){resultHint.testPosition=position;return true;}else if(numericType==C1NumericControlType.Currency&&input==culture.NumberFormat.CurrencySymbol){resultHint.testPosition=position;return true;}else{return false;}}}}
var aResult=true;position=this.getAdjustedPositionFromLeft(position);var aSlicePos=position;var currentText=C1NumericToStringFormat_.currentText;if(aSlicePos>currentText.length)
aSlicePos=currentText.length-1;if(input.length==1){if(currentText.charAt(aSlicePos)==input){resultHint.testPosition=aSlicePos;return true;}}
var aBegText=currentText.substring(0,aSlicePos);var aEndText=currentText.substring(aSlicePos,currentText.length);if(C1NumericToStringFormat_.IsZero()){aEndText=aEndText.replace(/[0]/,"");}
var sResultText=aBegText+input+aEndText;resultHint.testPosition=aBegText.length+input.length-1;C1NumericToStringFormat_.deFormatValue(sResultText);this.checkAndRepairBounds();try{if(input.length==1){if(useThousandsSeparator==true){var aNewBegText=C1NumericToStringFormat_.currentText.substring(0,aBegText.length);if(countSubstring(aNewBegText,C1NumericToStringFormat_.GroupSeparator)!=countSubstring(aBegText,C1NumericToStringFormat_.GroupSeparator)){resultHint.testPosition=resultHint.testPosition+1;}}else{var leftPrevCh=aBegText.charAt(aBegText.length-1);var leftCh=C1NumericToStringFormat_.currentText.charAt(resultHint.testPosition-1);if(leftCh!=leftPrevCh){resultHint.testPosition=resultHint.testPosition-1;}}}}catch(ex){}
return aResult;}
this.RemoveAt=function(startPosition,endPosition,resultHint){if(resultHint==undefined)
resultHint=new MaskedTextResultHint();resultHint.testPosition=startPosition;try{var currentText=C1NumericToStringFormat_.currentText;if((endPosition-startPosition==0)&&currentText.substring(startPosition,endPosition+1)==_NumberDecimalSeparator){return false;}
var aCurInsertText=currentText.slice(0,startPosition)+currentText.slice(endPosition+1);if(aCurInsertText=="")
aCurInsertText="0";C1NumericToStringFormat_.deFormatValue(aCurInsertText);if(startPosition==endPosition&&useThousandsSeparator==true){try{var aNewBegText=C1NumericToStringFormat_.currentText.substring(0,startPosition);if(countSubstring(aNewBegText,C1NumericToStringFormat_.GroupSeparator)!=countSubstring(aCurInsertText,C1NumericToStringFormat_.GroupSeparator)){resultHint.testPosition=resultHint.testPosition-1;if(currentText.indexOf(culture.NumberFormat.CurrencySymbol)==resultHint.testPosition||currentText.indexOf(culture.NumberFormat.PercentSymbol)==resultHint.testPosition){resultHint.testPosition=resultHint.testPosition+1;}}}catch(exIn){};}
this.checkAndRepairBounds();return true;}catch(e){}
this.checkAndRepairBounds();}
this.doIncrementEnumerationPart=function(position,resultHint,aIncVal){if(resultHint==undefined)
resultHint=new MaskedTextResultHint();C1NumericToStringFormat_.Increment(aIncVal);this.checkAndRepairBounds(true);}
this.doDecrementEnumerationPart=function(position,resultHint,aIncVal){if(resultHint==undefined)
resultHint=new MaskedTextResultHint();C1NumericToStringFormat_.Decrement(aIncVal);this.checkAndRepairBounds(true);}
this.set_CultureInfo=function(aCulture){culture=aCulture;C1NumericToStringFormat_=new C1NumericToStringFormat(culture,numericType,decimalDegitsPlaces,useThousandsSeparator);}
this.get_CultureInfo=function(){return culture;}
var additionalPostData="";this.get_value=this.get_Value=function(){return C1NumericToStringFormat_.getJSFloatValue();}
this.set_value=this.set_Value=function(aValue){try{C1NumericToStringFormat_.setValueFromJSFloat(aValue);this.checkAndRepairBounds(true);return true;}catch(ex){return false;}}
this.get_MinValue=function(){try{return minValue;}catch(ex){return null;}}
this.set_MinValue=function(aValue){try{minValue=parseFloat(aValue);minValueBool=true;additionalPostData+="|=MinValue|="+minValue;return true;}catch(ex){return false;}}
this.get_MaxValue=function(){try{return maxValue;}catch(ex){return null;}}
this.set_MaxValue=function(aValue){try{maxValue=parseFloat(aValue);maxValueBool=true;additionalPostData+="|=MaxValue|="+maxValue;return true;}catch(ex){return false;}}
this.get_ThousandsSeparator=function(){return useThousandsSeparator;}
this.set_ThousandsSeparator=function(aBoolValue){var t="0";if(C1NumericToStringFormat_!=undefined)
t=C1NumericToStringFormat_.getFormattedValue();useThousandsSeparator=toBool(aBoolValue);C1NumericToStringFormat_=new C1NumericToStringFormat(culture,numericType,decimalDegitsPlaces,useThousandsSeparator);C1NumericToStringFormat_.deFormatValue(t);additionalPostData+="|=ThousandsSeparator|="+useThousandsSeparator;}
this.get_DecimalPlaces=function(){return decimalDegitsPlaces;}
this.set_DecimalPlaces=function(aValue){decimalDegitsPlaces=aValue;var t="0";if(C1NumericToStringFormat_!=undefined)
t=C1NumericToStringFormat_.getFormattedValue();C1NumericToStringFormat_=new C1NumericToStringFormat(culture,numericType,decimalDegitsPlaces,useThousandsSeparator);C1NumericToStringFormat_.deFormatValue(t);additionalPostData+="|=DecimalPlaces|="+decimalDegitsPlaces;}
this.isValueNull=function(){return!this.checkAndRepairBounds(false,true);}
this.get_PostDataString=function(){var s="Value|="+c__escape(C1NumericToStringFormat_.getFormattedValue())+additionalPostData;return s;}
try{this.checkAndRepairBounds();}catch(ex){}}