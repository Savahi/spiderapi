Sub TableExport
  fileName = "1km_road_api.001.sprj"

  oScriptControl = CreateObject("MSScriptControl.ScriptControl")
  oScriptControl.Language = "JScript"  
  oScriptControl.AddCode "function getVal(jsonObj, propertyName) { return (propertyName in jsonObj) ? jsonObj[propertyName] : """"; }"
  oScriptControl.AddCode "function getValByIndex(jsonObj, index) { return (jsonObj.length > index) ? jsonObj[index] : """"; }"
  oScriptControl.AddCode "function getLength( jsonObj ) { return jsonObj.length; }"
  oScriptControl.AddCode "function getKeys( jsonObj ) { var keys = new Array(); for (var k in jsonObj) { keys.push(k); } return keys; } "

  oRequest = CreateObject("WinHttp.WinHttpRequest.5.1")  ' Object to make requests
  oRequest.Open "POST", "http://localhost:8080", false  ' Specifying Spider Project's API server name and port
  oRequest.SetTimeouts 0, 0, 0, 0             ' Waiting for reponse infinitely                                                                      

  oRequest.Send "{ ""command"":""openFile"", ""fileName"": """ + fileName + """ }"
  oResponse = oScriptControl.Eval("(" + oRequest.ResponseText + ")")    

  oRequest.Send "{ ""command"":""getTableHandle"", ""docHandle"":""" + oResponse.docHandle + """, ""table"":""GanttAct"" }"
  oResponse = oScriptControl.Eval("(" + oRequest.ResponseText + ")")    

  oRequest.Send "{ ""command"":""getTable"", ""tableHandle"":""" + oResponse.tableHandle + """ }"
  oResponse = oScriptControl.Eval("(" + oRequest.ResponseText + ")")

  oArray = oScriptControl.RUN("getVal", oResponse, "array")
  arrayLength = oScriptControl.RUN("getLength", oArray)

  oSheet = ThisComponent.GetCurrentController.ActiveSheet

  ' Obtaining keys from row 0 of the table read
  oRow0 = oScriptControl.RUN("getValByIndex", oArray, 0)
  oKeys = oScriptControl.RUN("getKeys", oRow0)
  keysNumber = oScriptControl.RUN("getLength", oKeys)

  ' Creating header: filling the first row of the sheet with key names
  FOR i = 0 TO keysNumber-1
    oCell = oSheet.getCellByPosition(i,0)
    oCell.String = oScriptControl.RUN("getValByIndex", oKeys, i)
  NEXT i

  FOR j = 0 TO arrayLength-1
    oRow = oScriptControl.RUN("getValByIndex", oArray, j)
    FOR i = 0 TO keysNumber-1
      key = oScriptControl.RUN("getValByIndex", oKeys, i)
      value = oScriptControl.RUN("getVal", oRow, key)
      oCell = oSheet.getCellByPosition(i,j+1)
      oCell.String = value
    NEXT i
  NEXT j  
End Sub