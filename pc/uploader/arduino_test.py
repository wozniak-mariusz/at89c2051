import unittest
import arduino

class ArduiniTests(unittest.TestCase):
    def test_dataFragmentIterator1(self):
        result = list(arduino.dataFragmentIterator(20, [0, 1, 2, 3]))
        self.assertEqual(result, [(0, [0, 1, 2, 3])])
        
    def test_dataFragmentIterator2(self):
        result = list(arduino.dataFragmentIterator(2, [0, 1, 2, 3]))
        self.assertEqual(result, [(0, [0, 1]), (2, [2, 3])])
        
    def test_dataFragmentIterator3(self):
        result = list(arduino.dataFragmentIterator(3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertEqual(result, [(0, [0, 1, 2]), (3, [3, 4, 5]), (6, [6, 7, 8]), (9, [9, 10])])
        
    def test_dataFragmentIterator4(self):
        result = list(arduino.dataFragmentIterator(10, [11, 22, 33]))
        self.assertEqual(result, [(0, [11, 22, 33])])

    def test_nibbleValueToText1(self):
        self.assertEqual(arduino.nibbleValueToText(0x0), '0')
        self.assertEqual(arduino.nibbleValueToText(0x1), '1')
        self.assertEqual(arduino.nibbleValueToText(0x2), '2')
        self.assertEqual(arduino.nibbleValueToText(0x3), '3')
        self.assertEqual(arduino.nibbleValueToText(0x4), '4')
        self.assertEqual(arduino.nibbleValueToText(0x5), '5')
        self.assertEqual(arduino.nibbleValueToText(0x6), '6')
        self.assertEqual(arduino.nibbleValueToText(0x7), '7')
        self.assertEqual(arduino.nibbleValueToText(0x8), '8')
        self.assertEqual(arduino.nibbleValueToText(0x9), '9')
        self.assertEqual(arduino.nibbleValueToText(0xa), 'a')
        self.assertEqual(arduino.nibbleValueToText(0xb), 'b')
        self.assertEqual(arduino.nibbleValueToText(0xc), 'c')
        self.assertEqual(arduino.nibbleValueToText(0xd), 'd')
        self.assertEqual(arduino.nibbleValueToText(0xe), 'e')
        self.assertEqual(arduino.nibbleValueToText(0xf), 'f')
 
    def test_dataToTextNibblesIterator1(self):
        result = list(arduino.dataToTextNibblesIterator([0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef]))
        self.assertEqual(result, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f' ])
        
    def test_iteratorToText1(self):
        result = arduino.iteratorToText(arduino.dataToTextNibblesIterator([0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef]))
        self.assertEqual(result, '0123456789abcdef')
        
    def test_iteratorToText2(self):
        result = arduino.iteratorToText(arduino.dataToTextNibblesIterator([0xaa, 0xbb, 0xcc]))
        self.assertEqual(result, 'aabbcc')
        
if __name__ == '__main__':
    unittest.main()