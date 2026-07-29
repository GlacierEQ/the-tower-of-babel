#include <iostream>
#include <vector>
#include <cmath>
class KVPruner { public: double entropy(double p) { return -p * std::log2(p); } };
