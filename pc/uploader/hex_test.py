import unittest
import hex

class HexTests(unittest.TestCase):
    def test_hexCharacterToValue1(self):
        self.assertEqual(hex.valueFromHexNibble('0'), 0)
        
    def test_hexCharacterToValue2(self):
        self.assertEqual(hex.valueFromHexNibble('1'), 1)
        
    def test_hexCharacterToValue3(self):
        self.assertEqual(hex.valueFromHexNibble('2'), 2)
        
    def test_hexCharacterToValue4(self):
        self.assertEqual(hex.valueFromHexNibble('3'), 3)
        
    def test_hexCharacterToValue5(self):
        self.assertEqual(hex.valueFromHexNibble('4'), 4)
        
    def test_hexCharacterToValue6(self):
        self.assertEqual(hex.valueFromHexNibble('5'), 5)
        
    def test_hexCharacterToValue7(self):
        self.assertEqual(hex.valueFromHexNibble('6'), 6)
        
    def test_hexCharacterToValue8(self):
        self.assertEqual(hex.valueFromHexNibble('7'), 7)
        
    def test_hexCharacterToValue9(self):
        self.assertEqual(hex.valueFromHexNibble('8'), 8)
        
    def test_hexCharacterToValue10(self):
        self.assertEqual(hex.valueFromHexNibble('9'), 9)
        
    def test_hexCharacterToValue11(self):
        self.assertEqual(hex.valueFromHexNibble('a'), 10)
        
    def test_hexCharacterToValue12(self):
        self.assertEqual(hex.valueFromHexNibble('A'), 10)
        
    def test_hexCharacterToValue13(self):
        self.assertEqual(hex.valueFromHexNibble('b'), 11)
        
    def test_hexCharacterToValue14(self):
        self.assertEqual(hex.valueFromHexNibble('b'), 11)
        
    def test_hexCharacterToValue15(self):
        self.assertEqual(hex.valueFromHexNibble('c'), 12)
        
    def test_hexCharacterToValue16(self):
        self.assertEqual(hex.valueFromHexNibble('C'), 12)
        
    def test_hexCharacterToValue17(self):
        self.assertEqual(hex.valueFromHexNibble('d'), 13)
        
    def test_hexCharacterToValue18(self):
        self.assertEqual(hex.valueFromHexNibble('D'), 13)
        
    def test_hexCharacterToValue19(self):
        self.assertEqual(hex.valueFromHexNibble('e'), 14)
        
    def test_hexCharacterToValue20(self):
        self.assertEqual(hex.valueFromHexNibble('E'), 14)
        
    def test_hexCharacterToValue21(self):
        self.assertEqual(hex.valueFromHexNibble('f'), 15)
        
    def test_hexCharacterToValue22(self):
        self.assertEqual(hex.valueFromHexNibble('F'), 15)

    def test_valueFromHexNibbleIterator1(self):
        self.assertEqual(list(hex.valueFromHexNibbleIterator('')), [])        
    
    def test_valueFromHexNibbleIterator2(self):
        self.assertEqual(list(hex.valueFromHexNibbleIterator('0')), [0])
        
    def test_valueFromHexNibbleIterator3(self):
        self.assertEqual(list(hex.valueFromHexNibbleIterator('1234')), [1, 2, 3, 4])
        
    def test_octetValueFromTwoNibleValuesIterator1(self):
        self.assertEqual(list(hex.octetValueFromTwoNibleValuesIterator([])), [])
        
    def test_octetValueFromTwoNibleValuesIterator2(self):
        self.assertRaises(AssertionError, lambda: list(hex.octetValueFromTwoNibleValuesIterator([1])))
        
    def test_octetValueFromTwoNibleValuesIterator3(self):
        self.assertEqual(list(hex.octetValueFromTwoNibleValuesIterator([0, 0xA])), [0xA])
        
    def test_octetValueFromTwoNibleValuesIterator4(self):
        it = hex.octetValueFromTwoNibleValuesIterator([1, 2, 0])
        self.assertEqual(it.next(), 0x12)
        self.assertRaises(AssertionError, it.next)
        
    def test_octetValueFromTwoNibleValuesIterator5(self):
        self.assertEqual(list(hex.octetValueFromTwoNibleValuesIterator([0xC, 0, 0xF, 0xF])), [0xC0, 0xFF])
        
    def test_octetValueFromTwoNibleValuesIterator6(self):
        self.assertRaises(AssertionError, lambda: list(hex.octetValueFromTwoNibleValuesIterator([-1, 0])))
        
    def test_octetValueFromTwoNibleValuesIterator7(self):
        self.assertRaises(AssertionError, lambda: list(hex.octetValueFromTwoNibleValuesIterator([0, 16])))
        
    def test_checksum1(self):
        self.assertRaises(hex.ChecksumException, lambda: hex.parseRecord(':03000000020800F4'))
        
    def test_unknownRecordType1(self):
        self.assertRaises(hex.UnknownRecordTypeException, lambda: hex.parseRecord(':030000ff020800F3'))
        
    def test_record1(self):
        (byteCount, address, recordType, data) = hex.parseRecord(':030000010208FAF8')
        
        self.assertEqual(byteCount, 3)
        self.assertEqual(address, 0)
        self.assertEqual(recordType, 1)
        self.assertEqual(data, [0x02, 0x08, 0xFA])
        
    def test_records1(self):
        lines = [
            ':03000000020800F3',
            ':0C080000787FE4F6D8FD75810702080C33',
            ':01080C0022C9',
            ':00000001FF',
        ]
        
        out = hex.parseRecords(lines)
        
        self.assertEqual(out[0x0000], 0x02)
        self.assertEqual(out[0x0001], 0x08)
        self.assertEqual(out[0x0002], 0x00)
        
        self.assertEqual(out[0x0800], 0x78)
        self.assertEqual(out[0x0801], 0x7F)
        self.assertEqual(out[0x0802], 0xE4)
        self.assertEqual(out[0x0803], 0xF6)
        self.assertEqual(out[0x0804], 0xD8)
        self.assertEqual(out[0x0805], 0xFD)
        self.assertEqual(out[0x0806], 0x75)
        self.assertEqual(out[0x0807], 0x81)
        self.assertEqual(out[0x0808], 0x07)
        self.assertEqual(out[0x0809], 0x02)
        self.assertEqual(out[0x080a], 0x08)
        self.assertEqual(out[0x080b], 0x0C)
        
        self.assertEqual(out[0x080c], 0x22)
        
    def test_missingEofRecord(self):
        lines = [
            ':03000000020800F3',
            ':0C080000787FE4F6D8FD75810702080C33',
            ':01080C0022C9',
        ]
        
        self.assertRaises(AssertionError, hex.parseRecords, lines)
        
    def test_eofRecordNotLast(self):
        lines = [
            ':03000000020800F3',
            ':01080C0022C9',
            ':0C080000787FE4F6D8FD75810702080C33',
        ]
        
        self.assertRaises(AssertionError, hex.parseRecords, lines)
        
if __name__ == '__main__':
    unittest.main()