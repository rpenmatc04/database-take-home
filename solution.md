
## Solution 

### Approach & Analysis

After running `./run_all.sh`, it was immediately clear from `queries.json` and the `query_distribution.png` output that queries were not sampled uniformly. Inspecting the code confirmed why: `constants.py` sets `LAMBDA_PARAM = 0.1`, and `generate_queries` samples targets from an exponential distribution (floored to integers), with `10` uniformly chosen starting nodes for the random walks. Because an exponential distribution is heavy-tailed, most targets are small indices. To quantify per-node hit rates, I wrote `scripts/visualize_probabilites.py`, producing `data/expected_query_counts.png` and `data/exponential_distribution.png`. The plots show that most queries fall in nodes `0–9`, roughly one-third land in 10–49, and `>99%` of the probability lies within the first 50 nodes.

Guided by this, my initial strategy built a single ring over nodes `0–49`, connecting each node `i` to `(i+1) mod 50`. Every node between 50 - 499 routed directly to node 0. This yielded a 100% success rate and a combined score of 520.

To exploit the finer structure of the probabilities, I then split the high-probability region into two rings: a tight inner ring (0–9) and a broader outer ring (10–49), while keeping the rule for nodes 50 - 499. I go into more detail about this approach in the following sections.

### Optimization Strategy

Given that most queries fall between nodes 0 and 9, I designed the graph to exploit this skew. Any node with a low likelihood of being hit (50–499) immediately routes to node 0, the single most probable target. Because starting nodes are chosen uniformly, this heuristic funnels us into the high-probability region as quickly as possible. Inside that region, each node Node `i` points to Node `i + 1` (not `i + 1 % 10`). I avoided a true ring structure because by arriving at Node `9` it very likely indicates that Nodes `0` to `9` have already been visited. Thus, it's more preferrable for the random walk to continue into the larger ring.

The larger ring (10–49) uses three edges per node to balance coverage and speed. Each node connects to its next node to sweep the ring in order, and also I added a “skip” successor (distance 5) to accelerate traversal given the fact that exponential grpah is heavy tailed. The chance that the very next node is the target drops quickly, so skipping ahead reduces expected path length. The third edge is low-probability and returns to node 0. This occasional reset matters when we start after the target but before node 50 and the true target lies back in 0–9, but it's quite rare (~`1/11` chance). The probability of a node in this ring going to Node 0 is much smaller than this because we make a decision at every Node (it's `1/18` at every node in the ring). The weights in this medium ring are biased heavily toward the next node, moderately toward the skip, and lightly toward the start.

### Implementation Details

The implementation is straightforward to follow with the comments in the code. There are two ring boundaries with a simple pointer for the inner ring and next, jump, or reset edges for the larger ring with Nodes `50-499` being set to `0` which is the most likely node. 

### Results

My optimized graph had a `100%` success rate (200/200), a median path length of `8.0` (200/200 queries), and a combined score of `542.26`. 

### Trade-offs & Limitations

There are intentional trade-offs. One tradeoff was that I only used `580` edges out of the given `1000`. This is because `450` of the nodes only have one edge to Node `0` (I explored multiple edges here see Iteration Journey) but there might be more to gain with these edges and more tuned skip edges. However, I did use the maximum edges per node `3` for the medium node! Additionally, I empirically tested the edge weights, but I would like to explore converting it to a linear program to optimize. 

The obvious tradeoff that was that some nodes are unreachable from other nodes. Currently, two nodes `A, B s.t A >= 50 and B >= 50` are disconnected, meaning that if we started at A or B we could not reach the other one. However, our success rate was still 100%. It's still a tradeoff because there is a nonzero probability that we would need to reach one of these such nodes. However, by making this decision we have massively reduced the path length. I could have potentially also finetuned the balance between success rate and path length by looking at the `compare_results()` score function, but the results were strong and I was happy with the `100%` success rate.

### Iteration Journey

I started by connecting every Node `i` to Node `(i + 1) % 500.` I knew this solution wasn't going to optimize reducing the path lengths, but I knew that it would have a 100% success rate as `MAX_DEPTH = 10000.` My assumption ended up being true as the success rate was 100% and the median path was `244.75` with a combined score of `210.07.` The median path increase was surprisingly a 50% improvement. 

Then, I worked on my first optimization that took advantage of the exponential distribution by making a singular large ring around Nodes 0 - 49 based on aformentioned findings about probability. This lead to making the algorithm significantly better, so much so that the final median path length was `8.0` while still having a 100% success rate. I was quite shocked by how good this was as I just wanted to use this as another baseline.

Afterward, I tried several ring configurations to reflect the varying probabilities across nodes, but none yielded meaningful gains. One idea mapped every node `i` in `50–499` to `i % 10` (and other mod variants). I also attempted to use the full 1,000-edge budget by giving these larger nodes two edges—one to node 0 (weight 10) and one to node 10 (weight 5), under the intuition that roughly two-thirds of queries fall in 0–9 and one-third in 10–49. In practice, this performed no better and sometimes worse than the single inner-ring approach. I experimented with multiple skip distances and weights to tune traversal speed, and with more time I would formalize this as an expected-value optimization over variable weights.

In conclusion, the most effective approach was to reach nodes 0–9 as quickly as possible, then sweep 10–49 rapidly. This simple strategy maintained a 100% success rate while keeping the median path length minimal. Along the way, I focused on bottlenecks, best- and worst-case behavior, and was ultimately fascinated by how a straightforward design, aligned with the sampling distribution, delivered the strongest results.

---