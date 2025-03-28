from verifier.countries import CountryVerifier
import re
from datetime import datetime

PROVINCES = [
    "ONTARIO",
    "MANITOBA",
    "BRITISH COLUMBIA",
    "ALBERTA",
    "QUEBEC",
    "NEWFOUNDLAND AND LABRADOR",
    "NEW BRUNSWICK",
    "NOVA SCOTIA",
    "SASKATCHEWAN",
    "NORTHWEST TERRAINS",
    "NUNAVUT",
    "YUKON"
]



class DriversLicense:
    def __init__( self, textData ):
        self.textData = textData
        self.documentType = ""
        self.idNumber = ""
        self.fullName = ""
        self.dob = ""
        self.gender = ""
        self.nationality = ""
        self.address = ""
        self.issuedDate = ""
        self.expiryDate = ""
        self.province = ""
        self.__extractData()

    def convert_date_format( self, date_str ):
        # Parse the input string
        date_obj = datetime.strptime( date_str, "%Y/%m/%d" )
        # Format to YYYY-MM-DD for HTML date input
        return date_obj.strftime( "%Y-%m-%d" )

    def __extractData( self ):
        if self.__getDocumentType() == "Driver's License":
            self.documentType = "Driver's License"
            self.province = self.__getProvince()
            self.idNumber = self.__getIdNumber()
            self.fullName = self.__getFullName()
            self.dob = self.__getDob()
            self.gender = self.__getGender()
            self.nationality = self.__getNationality()
            self.address = self.__getAddress()
            self.issuedDate = self.__getIssuedDate()
            self.expiryDate = self.__getExpiryDate()
            if self.dob:
                self.dob = self.convert_date_format( self.dob )
            if self.issuedDate:
                self.issuedDate = self.convert_date_format( self.issuedDate )
            if self.expiryDate:
                self.expiryDate = self.convert_date_format( self.expiryDate )

    def __getDocumentType( self ):
        for text in self.textData:
            isDriversLicense = re.search( r"DRIVER'[S$]\s*LICENCE", text, re.IGNORECASE )
            if isDriversLicense:
                return "Driver's License"
        return "Unknown"

    def __getProvince( self ):
        for text in self.textData:
            if text in PROVINCES:
                return text
        return ""

    def __getFullName( self ):
        i = 0
        while i < len( self.textData ):
            if "NAME" in self.textData[i]:
                fullName = ""
                while i < len( self.textData ):
                    name = re.search( r"^(([A-Z]+)\s*)+", self.textData[i + 1], re.IGNORECASE )
                    if name:
                        fullName += name.group(0).strip() + " "
                    else:
                        break
                    i += 1
                return fullName.strip()
            i += 1
        i = 0
        while i < len( self.textData ) and i < 10:
            num = re.search( r"^1[\.,]?2\s+(\w*)", self.textData[i], re.IGNORECASE )
            if num:
                fullName = num.group(1).strip()
                fullName += " " if fullName else ""
                j = i + 1
                max = j if fullName else j + 1
                while j < len( self.textData ) and j <= max:
                    name = re.search( r"^(([A-Z]+)\s*)+", self.textData[j], re.IGNORECASE )
                    if name:
                        fullName += name.group(0).strip() + " "
                    else:
                        break
                    j += 1
                return fullName.strip()
            i += 1
        return ""

    def __getDob( self ):
        for i in range( len( self.textData ) ):
            dob = re.search( r"\d{4}/\d{2}/\d{2}", self.textData[i], re.IGNORECASE )
            if dob and "DOB" in self.textData[i - 1]:
                return dob.group(0)
        return ""

    def __getGender( self ):
        gender = "Unknown"
        for text in self.textData:
            _text = text.strip()
            if _text == "M":
                gender = "Male"
            elif _text == "F":
                gender = "Female"
        return gender

    def __getNationality( self ):
        return ""


    def __getAddress( self ):
        if self.fullName:
            lastName = self.fullName.split()[-1]
            for i in range( len( self.textData ) ):
                if lastName in self.textData[i]:
                    return self.textData[i + 1].strip() + " " + self.textData[i + 2].strip()                
        return ""

    def __getIssuedDate( self ):
        for i in range( len( self.textData ) ):
            date = re.search( r"\d{4}/\d{2}/\d{2}", self.textData[i], re.IGNORECASE )
            if date and "DOB" not in self.textData[i - 1]:
                return date.group(0)
        return ""

    def __getExpiryDate( self ):
        if self.issuedDate:
            start = False
            for i in range( len( self.textData ) ):
                if self.issuedDate == self.textData[i]:
                    start = True
                    continue
                if start:
                    dob = re.search( r"\d{4}/\d{2}/\d{2}", self.textData[i], re.IGNORECASE )
                    if dob and "DOB" not in self.textData[i - 1]:
                        return dob.group(0)
        return ""

    def __getIdNumber( self ):
        for i in range( len( self.textData ) ):
            text = self.textData[i]
            if "ISS" in text and "DEL" in text:
                min = i - 5
                j = i - 1
                idNumber = ""
                while j >= min:
                    part = self.textData[j]
                    if "NUMER" in part or "PERMIS" in part:
                        break
                    idNumber = part.strip() + idNumber
                    j -= 1
                return idNumber
        return ""

    

    def toDict( self ):
        return {
            "DocumentType": self.documentType,
            "IdNumber": self.idNumber,
            "FullName": self.fullName,
            "DateOfBirth": self.dob,
            "Gender": self.gender,
            "Nationality": self.nationality,
            "Address": self.address,
            "IssuedDate": self.issuedDate,
            "ExpiryDate": self.expiryDate,
            "Province": self.province
        }




class Verifier( CountryVerifier ):
    def __init__( self ):
        super().__init__( "Canada" )

    def verify( self, textData, userData ):  
        result = self.defaultResult()
        textData = [ line.upper() for line in textData ]
        if userData["docType"] == "DL":
            idInfo = DriversLicense( textData ).toDict()
            result["idInfo"] = idInfo
            if idInfo["FullName"] and idInfo["IdNumber"] and idInfo["DateOfBirth"]:
                result["validId"] = True
                result["verifiedId"] = True
            else:
                missing = []
                if not idInfo["FullName"]: missing.append( "Name" )
                if not idInfo["IdNumber"]: missing.append( "ID Number" )
                if not idInfo["DateOfBirth"]: missing.append( "Date of Birth" )
                result["message"] = f"Missing information ( { ', '.join( missing ) } )"
        return result

    def extractData( self, textData, docType = "DL" ):
        if docType == "DL":
            return DriversLicense( textData ).toDict()
        return {}
