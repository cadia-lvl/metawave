import matplotlib.pyplot as plt

def a(n, seq):
    '''
        n = 0 : a(n) = 0
        n > 0 : a(n) = 
            * a(n-1) - n, if not in sequence already
            * a(n-1) + n, otherwise
    '''
    if n == 0:
        return 0
    elif seq[n-1] - n > 0 and seq[n-1] - n not in seq:
        return seq[n-1] - n
    else:
        return seq[n-1] + n 


if __name__ == '__main__':
    num = 200
    seq = []
    for n in range(num):
        v = a(n, seq)
        seq.append(v)
    #plt.scatter(seq, [0 for _ in range(100)])
    fig, ax = plt.subplots()
    data = []
    flip = True
    for i in range(num - 1):
        p1 = seq[i]
        p2 = seq[i+1]
        rad = (i+1)/2
        c = p1 + rad if p1 < p2 else p1 - rad
        p = [c, - rad if flip else rad]
        flip = not flip
        data += [[p1, 0], p]
    for i in range(num - 1):
        plt.plot([data[i][0], data[i+1][0]], [data[i][1], data[i+1][1]], color='k')
    plt.tight_layout()
    plt.show()