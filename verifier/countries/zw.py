
from verifier.countries import CountryVerifier


class Verifier( CountryVerifier ):
    def __init__( self ):
        super().__init__( "Zimbabwe" )

    def verify( self, textData, userData ):        
        result = super().verify( textData, userData, ["name"] )
        return result