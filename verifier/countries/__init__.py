
class CountryVerifier:

    def __init__( self, name ):
        self.name = name

    def defaultResult( self ):        
        return {
            "idInfo": {},
            "validId": False,
            "verifiedId": False
        }

    def verify( self, textData, data, required = [] ):
        result = self.defaultResult()
        textData = "\n".join( textData )

        _textData = textData.upper()
        
        for field in required:
            if field not in data:
                result["message"] = f"Required field { field } not provided"
                return result
            value = data[field]
            valid = False

            values = []
            for v in value.split():
                values.append( v.upper() )


            valid = True
            for v in values:
                if v not in _textData:
                    valid = False
                    break                

            if not valid:
                result["message"] = f"{field} not found / mismatch on ID"
                return result
                

        result["validId"] = True
        result["verifiedId"] = True
        return result

    def extractData( self, textData, docType = "DL" ):
        return {}
    
    

    