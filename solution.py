import sys
import os
import hashlib

def get_file_info(path):
    with open(path, 'rb') as f:
        data = f.read()
    size = len(data)
    digest = hashlib.sha256(data).hexdigest()
    hist = [0] * 256
    for b in data:
        hist[b] += 1
    return digest, size, hist

def common_ratio(hist1, hist2, size1, size2):
    common = 0
    for i in range(256):
        if hist1[i] < hist2[i]:
            common += hist1[i]
        else:
            common += hist2[i]
    if size1 > size2:
        denom = size1
    else:
        denom = size2
    if denom == 0:
        return 0.0
    return common / denom

def main():
    args = sys.argv[1:]
    if len(args) >= 3:
        dir1 = args[0]
        dir2 = args[1]
        try:
            threshold = float(args[2])
        except:
            threshold = 0.0
    else:
        dir1 = input().strip()
        dir2 = input().strip()
        threshold = float(input().strip())
    files1 = []
    files2 = []
    for name in os.listdir(dir1):
        p = os.path.join(dir1, name)
        if os.path.isfile(p):
            files1.append(name)
    for name in os.listdir(dir2):
        p = os.path.join(dir2, name)
        if os.path.isfile(p):
            files2.append(name)
    info1 = {}
    info2 = {}
    for name in files1:
        digest, size, hist = get_file_info(os.path.join(dir1, name))
        info1[name] = (digest, size, hist)
    for name in files2:
        digest, size, hist = get_file_info(os.path.join(dir2, name))
        info2[name] = (digest, size, hist)
    identical = []
    identical_set = set()
    for n1, (d1, s1, h1) in info1.items():
        for n2, (d2, s2, h2) in info2.items():
            if d1 == d2 and s1 == s2:
                identical.append((n1, n2))
                identical_set.add((n1, n2))
    similar = []
    for n1, (d1, s1, h1) in info1.items():
        for n2, (d2, s2, h2) in info2.items():
            if (n1, n2) in identical_set:
                continue
            ratio = common_ratio(h1, h2, s1, s2) * 100.0
            if ratio >= threshold:
                similar.append((n1, n2, ratio))
    used1 = set()
    used2 = set()
    for n1, n2 in identical:
        used1.add(n1)
        used2.add(n2)
    for n1, n2, _ in similar:
        used1.add(n1)
        used2.add(n2)
    only1 = [n1 for n1 in files1 if n1 not in used1]
    only2 = [n2 for n2 in files2 if n2 not in used2]
    for n1, n2 in identical:
        print(f"{dir1}/{n1} - {dir2}/{n2}")
    for n1, n2, r in similar:
        if r % 1 == 0:
            pr = int(r)
        else:
            pr = round(r, 2)
        print(f"{dir1}/{n1} - {dir2}/{n2} - {pr}")
    for n1 in only1:
        print(f"{dir1}/{n1}")
    for n2 in only2:
        print(f"{dir2}/{n2}")

if __name__ == "__main__":
    main()