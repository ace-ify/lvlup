# System Design Cheatsheet for Job Interviews

> *Source: https://cheatsheet.dennyzhang.com/cheatsheet-systemdesign-A4 (Updated: June 7, 2020)*

---

## Reference Resources

| Type | Name |
|------|------|
| YouTube | Intro to Architecture and Systems Design Interviews |
| YouTube | Success in Tech Channel |
| YouTube | Scalability — Harvard Web Development |
| Papers | CheatSheet: Well-Known Papers For IT Industry |
| GitHub | donnemartin/system-design-primer |
| GitHub | checkcheckzz/system-design-interview |
| GitHub | yangshun/tech-interview-handbook |
| Website | hiredintech — System Design |
| Website | blog.gainlo.co |
| Website | interviewing.io |
| Blog | highscalability |
| Blog | All Things Distributed (Amazon CTO) |
| Blog | Netflix, Airbnb, Instagram Engineering (Medium) |

---

## Design Problems by Category

| # | Category | Examples |
|---|----------|----------|
| 1 | K/V DB Store | Design Memcache/Redis |
| 2 | Data Synchronization | Design Dropbox client sync |
| 3 | Resource/Task Scheduling | Web crawler, Delayed task queue, Distributed message queue |
| 4 | Distributed Component | Distributed hit counter, UUID generator |
| 5 | SNS System | Design Twitter News Feed |
| 6 | API Gateway | Design an API Rate Limiter |
| 7 | Logging & Metrics | Pull vs Push model |
| 8 | Gaming System | Leaderboard Ranking |
| 10 | Small-scale MIS | Flight booking service, Payment processor |
| 11 | Recommendation System | Amazon book recommendation |
| 12 | Communication System | Message chat room |
| 13 | Ads System | — |

---

## Top 31 Component Design Problems

1. Top K Frequent Elements in Recent X mins
2. Design an API Rate Limiter
3. Design: Leaderboard Ranking
4. Delayed Task Queue
5. Spam Filter: block malicious IPs
6. Find duplicate files across 1000 servers (10M files)
7. Design a monitoring system for 10,000 nodes
8. Design a scalable notification service
9. Web crawler for 1 billion URLs
10. Design Twitter timeline feature
11. How to upload large videos at scale
12. Real-time Deduping at Scale
13. How quorum-based DB works
14. Implement Redis clustering
15. Deploy 1GB binary to 10,000 servers
16. Distribute TB data to 10,000 nodes
17. Merge big datasets across different servers
18. Unique URL hits
19. Design a distributed counter
20. Design a distributed message queue
21. Design a distributed cache service
22. Design a distributed Hashmap
23. Design a distributed UUID generator
24. Design a Git service
25. Design: A Parking Lot Service
26. Design a distributed transaction
27. Design: A URL Redirecting Feature
28. Store 2TB data with redundancy on three 1TB disks (XOR bit manipulation)
29. Support `diff big1.bin big2.bin` — LCS (Longest Common Subsequence)
30. Support `rsync big1.bin ssh:/big2.bin` in poor network — Delta transfer algorithm
31. Avoid double payment in a distributed payment system

---

## Top 31 Product Design Problems

1. Design TinyURL — URL Shortener
2. Design Twitter News Feed
3. Design K/V DB
4. Design Autocomplete / Typeahead
5. Design an online contest system (like LeetCode)
6. Design Google Calendar
7. Design a Load Balancer
8. Design: Flight Booking Service
9. Design: Uber Backend
10. Design: An Elevator Service
11. Design Amazon Shopping Cart
12. Design: Google Suggestion Service
13. Design a Payment Processor
14. Design Google Docs
15. Design Gmail
16. Design RSS News Reader
17. Design a rich document editor (client-server API)
18. Design Instagram (photo sharing)
19. Design Yelp (location-based system)
20. Design Pastebin.com
21. Design Amazon Book Recommendation
22. Design Google PageRank
23. Design Messaging/Notification System
24. Design Memcache/Redis
25. Design a Voice Conference System
26. Design an API Gateway
27. Design Slack
28. Design a service auto-discovery feature
29. Design a secrets management system
30. Design Google AdSense fraud detection
31. Design The Great Firewall

---

## Process of System Design

| Step | Name | Summary |
|------|------|---------|
| 1 | Outline Use Cases | List major use cases; questions you ask define your level |
| 2 | Estimate Scale | Back-of-the-envelope estimation (data + traffic) |
| 3 | Define Data Model | Clarify how data flows among components |
| 4 | Abstract Design | Sketch main components; avoid going too deep initially |
| 5 | Detailed Design | Explain trade-offs; deep dive on demand |
| 6 | Identify Bottlenecks | Key challenges + trade-offs (usually no optimal solution) |
| 7 | Scale Your Design | Availability, Resiliency, Scalability, Security, Serviceability |
| 8 | Show Relevant Experience | Industry best practices; your scaling/trade-off/resiliency experience |

---

## Common Mistakes in System Design

| # | Mistake | Why It's Bad |
|---|---------|-------------|
| 1 | Running into an opinionated solution before clarification | Hard to communicate; shows inexperience |
| 2 | Not driving the conversation | Shows inexperience |
| 3 | General answers without personal experience | Lacks depth |
| 4 | Being stubborn | Makes interviewers uncomfortable |

---

## Top 30 Concepts for Feature/System Design

| # | Concept | Summary |
|---|---------|--------|
| 1 | Caching | Stores data for faster future retrieval |
| 2 | Message Queue | Async communications protocol |
| 3 | Data Partitioning & Sharding | Break big data volume into smaller parts |
| 4 | DB Indexing | Indexes on columns to speed up lookups |
| 5 | DB Replication | Duplicate data to increase availability |
| 6 | CAP Theorem | Consistency / Availability / Partition (pick 2 of 3) |
| 7 | SQL & NoSQL | Relational vs non-relational databases |
| 8 | Concurrency & Communication | — |
| 9 | Pessimistic & Optimistic Locking | — |
| 10 | Consistency Models | Weak, eventual, strong consistency |
| 11 | Conflict Resolution | Quorum, vector lock, CRDTs |
| 12 | B+ Tree | — |
| 13 | Networking: HTTP | — |
| 14 | Networking: TCP/UDP | — |
| 15 | Pull vs Push Model | — |
| 19 | Self-Protection | API Rate limit, Circuit breaker, Bulkhead, Throttling |
| 22 | Load Balancer | — |
| 23 | Scale Up vs Scale Out | Vertical vs Horizontal scaling |
| 27 | Consistency Patterns | Weak, Eventual, Strong |
| 28 | Availability Patterns | Failover vs Replication |
| 29 | CDN | Edge caching |
| 32 | DNS | — |

---

## Top 26 Advanced Data Structures & Algorithms

| # | Name | Summary |
|---|------|---------|
| 1 | Consistent Hash | — |
| 2 | Bloom Filter | Space-efficient; returns "possibly in set" or "definitely not" |
| 3 | HyperLogLog | Count-distinct estimation with ~98% accuracy |
| 4 | Reservoir Sampling | — |
| 5 | Merkle Tree | — |
| 6 | LPM (Longest Prefix Match) | — |
| 8 | Gossip Protocol | Propagate cluster status |
| 9 | Vector Clocks | — |
| 11 | Skip List | — |
| 12 | CRDTs | Conflict-Free Replicated Data Types |
| 15 | SSTable | Sorted Strings Table |
| 17 | LSM Trees | Log Structured Merge Trees |
| 18 | Two-phase / Three-phase Commit | — |
| 19 | Paxos and Raft Protocol | — |
| 21 | Cuckoo Hashing | Resolves hash collisions with worst-case constant lookup |
| 22 | Snappy/LZSS | Fast data compression/decompression |
| 24 | Geohash | — |
| 25 | Quadtree | — |
| 26 | DHT | Distributed Hash Table |

---

## Cloud Design Principles

| # | Principle |
|---|-----------|
| 1 | Fail fast |
| 2 | Design for failure |
| 3 | Immutable infrastructure |
| 4 | Cats vs Cattle (avoid snowflake servers) |
| 5 | Auto healing |
| 6 | Async programming |
| 7 | GitOps operational model |
| 8 | Event-Driven Architectures |

---

## Cloud Design Patterns

| Pattern | Description |
|---------|-------------|
| Ambassador | Helper service to send network requests alongside main service |
| Cache-Aside | Load data on demand into a cache from a data store |
| Circuit Breaker | Abort a request if it takes too many resources |
| Bulkhead | Isolate elements into pools so one failure doesn't burn all |
| Gateway Aggregation | Aggregate multiple individual requests into one |
| Priority Queue | Support different SLAs for different clients |
| Strangler | Incrementally migrate a legacy system piece by piece |

---

## Engineering of Well-Known Products

| Company | Resource |
|---------|----------|
| Google | Google Architecture |
| Facebook | Facebook Live Streams |
| Twitter | Twitter Image Service; Timelines at Scale |
| Uber | Lessons Learned From Scaling Uber |
| Tumblr | Tumblr Architecture |
| StackOverflow | Stack Overflow Architecture |

---

## How to Grow Design Expertise Daily

1. Keep curiosity — think about interesting/weird problems
2. Deep dive into your daily work
3. Learn from your colleagues
4. Study popular products under the hood
5. Read engineering blogs (especially big companies)
6. Understand tools under the hood
7. Try new tools: use cases, alternatives, pros/cons
8. Read research papers
9. Gain hands-on experience
10. Learn how databases and OSes work
11. Deep dive into one programming language

---

## Additional Resources

- https://github.com/binhnguyennus/awesome-scalability
- https://highscalability.com
- https://docs.microsoft.com/en-us/azure/architecture/patterns/
- https://github.com/sdmg15/Best-websites-a-programmer-should-visit
