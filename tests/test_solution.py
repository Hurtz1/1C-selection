import os
import sys
import tempfile
import subprocess
import unittest

class SolutionTestCase(unittest.TestCase):
    def run_solution(self, dir1, dir2, threshold):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'solution.py'))
        result = subprocess.run([
            sys.executable, script_path, dir1, dir2, str(threshold)
        ], capture_output=True, text=True)
        output = result.stdout.strip()
        if not output:
            return []
        return [line.strip() for line in output.splitlines()]

    def parse_identical(self, line):
        parts = line.split(' - ')
        if len(parts) == 2:
            return os.path.basename(parts[0]), os.path.basename(parts[1])
        return None

    def parse_similar(self, line):
        parts = line.split(' - ')
        if len(parts) == 3:
            try:
                return os.path.basename(parts[0]), os.path.basename(parts[1]), float(parts[2])
            except ValueError:
                return None
        return None

    def test_identical_files(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, 'f1.bin'), 'wb') as f:
                f.write(b'ABC')
            with open(os.path.join(d2, 'f2.bin'), 'wb') as f:
                f.write(b'ABC')
            lines = self.run_solution(d1, d2, 50)
            self.assertEqual(len(lines), 1)
            ident = self.parse_identical(lines[0])
            self.assertIsNotNone(ident)
            a, b = ident
            self.assertEqual(set([a, b]), {'f1.bin', 'f2.bin'})

    def test_similar_files(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, 'a.bin'), 'wb') as f:
                f.write(b'ABA')
            with open(os.path.join(d2, 'b.bin'), 'wb') as f:
                f.write(b'BA')
            lines = self.run_solution(d1, d2, 50)
            self.assertEqual(len(lines), 1)
            sim = self.parse_similar(lines[0])
            self.assertIsNotNone(sim)
            a, b, ratio = sim
            self.assertEqual(set([a, b]), {'a.bin', 'b.bin'})
            self.assertAlmostEqual(ratio, 66.6666, delta=0.1)

    def test_unique_files(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, 'x.bin'), 'wb') as f:
                f.write(b'ABC')
            with open(os.path.join(d2, 'y.bin'), 'wb') as f:
                f.write(b'DEF')
            lines = self.run_solution(d1, d2, 50)
            self.assertEqual(len(lines), 2)
            names = set()
            for line in lines:
                parts = line.split('/')
                name = parts[-1]
                names.add(name)
            self.assertEqual(names, {'x.bin', 'y.bin'})

    def test_multiple_identical(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, 'aa.bin'), 'wb') as f:
                f.write(b'AAA')
            with open(os.path.join(d1, 'bb.bin'), 'wb') as f:
                f.write(b'BBB')
            with open(os.path.join(d2, 'c1.bin'), 'wb') as f:
                f.write(b'AAA')
            with open(os.path.join(d2, 'c2.bin'), 'wb') as f:
                f.write(b'BBB')
            lines = self.run_solution(d1, d2, 50)
            self.assertEqual(len(lines), 2)
            ident_pairs = set()
            for line in lines:
                ident = self.parse_identical(line)
                self.assertIsNotNone(ident)
                a, b = ident
                ident_pairs.add((a, b))
            expected = {('aa.bin', 'c1.bin'), ('bb.bin', 'c2.bin')}
            observed_names = {frozenset(pair) for pair in ident_pairs}
            expected_names = {frozenset(pair) for pair in expected}
            self.assertEqual(observed_names, expected_names)

    def test_threshold_effect(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            with open(os.path.join(d1, 'a.bin'), 'wb') as f:
                f.write(b'ABA')
            with open(os.path.join(d2, 'b.bin'), 'wb') as f:
                f.write(b'BA')
            lines = self.run_solution(d1, d2, 70)

            self.assertEqual(len(lines), 2)
            names = set()
            for line in lines:
                parts = line.split('/')
                name = parts[-1]
                names.add(name)
            self.assertEqual(names, {'a.bin', 'b.bin'})


if __name__ == '__main__':
    unittest.main()