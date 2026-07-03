# Computer Network Notes for Placements and GATE

---

## IP Addressing

### IP Address Classes

| Class | First Bits | Network Bits | Host Bits | Range |
|-------|-----------|--------------|-----------|-------|
| A | 0 | 8 | 24 | 1–126 |
| B | 10 | 16 | 16 | 128–191 |
| C | 110 | 24 | 8 | 192–223 |
| D | 1110 | — | — | 224–239 (Multicast) |
| E | 1111 | — | — | 240–255 (Research) |

- **Network Mask:** Class A = 255.0.0.0, Class B = 255.255.0.0, Class C = 255.255.255.0
- **0** → DHCP client; **127** → Loopback address
- For Network ID: all host bits = 0
- For DBA (Directed Broadcast Address): all host bits = 1

### Private IP Ranges
- 10.0.0.0 – 10.255.255.255
- 172.16.0.0 – 172.31.255.255
- 192.168.0.0 – 192.168.255.255

### NAT (Network Address Translation)
- NAT router converts private IP → public IP (outgoing), and public IP → private IP (incoming).
- A computer can have multiple IP addresses at different instances of time.
- A computer can have multiple MAC addresses to support fault tolerance.

---

## Subnetting

### Example 1
**IP:** 199.48.98.99 | **Subnet Mask:** 255.255.255.224

- Subnet ID: 199.48.98.96 (bitwise AND of IP & mask)
- No. of Subnets: 2³ – 2 = 6
- No. of Hosts per Subnet: 2⁵ – 2 = 30
- 1st Subnet ID: 199.48.98.32
- 2nd Subnet ID: 199.48.98.64
- 1st host of 1st Subnet: 199.48.98.33
- Last host of 1st Subnet: 199.48.98.62
- DBA of 1st Subnet: 199.48.98.63

> **NOTE:** Wherever there are continuous 1s in the mask, use the (x+32) formula to calculate further subnet IDs.

---

## Networking Devices

| Device | Broadcast Domain | Collision Domain | Notes |
|--------|-----------------|-----------------|-------|
| Hub / Repeater | Not separator | Not separator | Passive device |
| Bridge | Not separator | Separator | Connects similar networks |
| Switch (Datalink layer) | Not separator | Separator | Maintains lookup table for forwarding frames |
| Router | Separator | Separator | WAN device, operates on IP; connects dissimilar networks |
| Gateway | Separator | Separator | Multiprotocol converter; highly sophisticated router |

---

## IPv4 vs IPv6

| Feature | IPv4 | IPv6 |
|---------|------|------|
| Protocol type | Stateful (by default) | Stateless (by default) |
| Speed | Slower | Faster |
| ARP | Required | Not required (MAC is part of IPv6 address) |
| DHCP | Required | Not required (stateless auto-configuration) |
| NAT | Required | Not required |
| Broadcasting | Supported | Not supported (only Multicasting & Anycasting) |
| Multiple IPs | One at a time | Multiple IPs at the same time |

- **Anycasting (IPv6):** All nodes share the same address; service is provided by the nearest node.
- Best suited for mobile and wireless networks due to stateless auto-configuration.

---

## PING & Loopback

- **PING (Packet Internet Gropher):** Uses ICMP to test reachability of a system in the network.
- **Loopback Address (127.x.x.x):** Used for troubleshooting self-computer. It never enters the network; always stays as the Destination address.
- Even without an assigned IP, a computer can be troubleshot using DHCP client and Loopback Address.

---

## Circuit Switching vs Packet Switching

| Feature | Circuit Switching | Packet Switching |
|---------|-------------------|------------------|
| Phases | Connection establishment → Data transfer → Connection release | Direct data transfer |
| Path | Entire path is decided upfront | Each packet has destination address; path decided by router |
| Technique | Not store-and-forward | Store-and-forward |
| Delay | Uniform between data units | Variable between data units |
| Resource Reservation | Yes | No (resources are shareable) |
| Resource Wastage | More | Less |
| Congestion | During connection establishment | During data transfer phase |
| Fault Tolerance | No (packets can't be diverted) | Yes (packets can be re-routed) |
| Use case | Long messages, reliable | Short messages, fast |

---

## OSI Model

| Layer # | Layer Name | PDU | Address | Key Devices | Key Protocols |
|---------|-----------|-----|---------|-------------|---------------|
| 7 | Application | Message | — | Gateway | HTTP, FTP, SMTP, DNS, Telnet |
| 6 | Presentation | Message | — | Gateway | Syntax/Semantics |
| 5 | Session | Message | — | Gateway | Dialog control |
| 4 | Transport | Segment / Datagram | Port Address | Gateway | TCP, UDP |
| 3 | Network | Packet | IP Address (WAN) | Router, 3-layer switch | IP, ICMP |
| 2 | Data Link | Frame | MAC Address (LAN) | Bridge, 2-layer switch | ARP, RARP |
| 1 | Physical | Bits | — | Hub, Repeater | — |

- **Data Link Layer:** Node-to-node delivery within LAN.
- **Network Layer:** Source-to-destination delivery between networks.
- **Transport Layer:** Process-to-process (end-to-end) delivery. Identified by Port Address.
- **Socket Address** = IP Address + Port Number.

### IEEE 802 Standards

| Standard | Description |
|----------|-------------|
| 802.1 | Higher layer LAN protocols |
| 802.2 | LLC |
| 802.3 | Ethernet |
| 802.5 | Token Ring MAC |
| 802.11 | Wireless LAN (Wi-Fi) |
| 802.15 | Wireless PAN (Bluetooth) |
| 802.16 | Wireless MAN |

---

## TTL (Time to Live)

- 8-bit field in IP header.
- Decremented by 1 each time a packet passes through a router.
- When TTL reaches 0, the packet is dropped and ICMP sends a "Time Exceeded" message to the source.
- In practice, TTL acts as a hop count. Guarantees packet stays in network ≤ 255 seconds.

---

## ICMP (Internet Control Message Protocol)

### Error Messages
1. **Source Quench:** Router buffer full → ICMP notifies source to reduce transmission speed.
2. **Parameter Problem:** Header bits corrupted during transmission → packet dropped, source notified.
3. **Time Exceeded:** Fragment holding timer expires → fragments dropped.
4. **Destination Unreachable:** Sent by router or destination host when packet can't be delivered.
5. **Redirection Message:** Packet forwarded in wrong direction → ICMP redirects with correct path.

### Query Messages
1. **Echo Request / Reply:** Used for PING to determine if two systems can communicate.
2. **Timestamp Request / Reply:** Determines RTT (Round Trip Time) needed for an IP datagram.

---

## TCP Timers

| Timer | Purpose |
|-------|---------|
| Timeout (Retransmission) Timer | Dynamic timer; retransmits segment if ACK not received before expiry |
| Time Wait Timer | Used during connection termination; prevents just-closed port from reopening quickly |
| Keep Alive Timer | Prevents long idle connections; server sends 10 probe segments if no response for 2 hours |
| Persistent Timer | Deals with zero-window-size deadlock; keeps window size information flowing |

---

## TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| Header | Dynamic (20–60 bytes) | Fixed (8 bytes) |
| Connection | Connection-oriented | Connectionless |
| Sequence Numbers | Yes | No |
| Flow Control | Yes | No |
| Error Control | Yes | Optional |
| Speed | Slow | Fast |
| Multicasting/Broadcasting | No | Yes |
| Checksum | Mandatory | Optional |
| Use Cases | HTTP, FTP, SMTP, Telnet | TFTP, DNS, SNMP |

### Common Port Numbers

| Protocol | Port |
|----------|------|
| DNS | TCP/UDP 53 |
| HTTP | TCP 80 |
| SMTP | TCP 25 |
| POP3 | UDP 110 |
| Telnet | TCP 23 |
| FTP | TCP 20 (data), 21 (control) |
| DHCP | UDP 67 |

---

## Application Layer Protocols

### HTTP
- Client-server, synchronous protocol. Port 80. Stateless.
- **Persistent HTTP:** Multiple objects over one connection.
- **Non-Persistent HTTP:** Separate connection per object (more secure).
- **HTTP Methods:** GET, POST, PUT, HEAD, CONNECT, TRACE, OPTIONS

### FTP (File Transfer Protocol)
- Control connection on Port 21 (stays open).
- Separate data connection on Port 20 (closed after file download).
- Authorized users only; uses TCP.

### TFTP (Trivial FTP)
- Uses UDP, allows anonymous users, has flow control at Application Layer.

### SMTP (Simple Mail Transfer Protocol)
- Text-based push protocol. Port 25. Uses TCP.
- MIME Extension allows graphical data via SMTP.
- **POP3 / IMAP4** = Pull protocols (retrieve mail from server).
  - POP3: All mails are equal/serial.
  - IMAP4: Mails can be kept in hierarchy; provides security.

---

## IPv4 Header Format

```
| VER (4) | HLEN (4) | Service (8) | Total Length (16) |
| Identification (16) | Flags (3) | Fragment Offset (13) |
| TTL (8) | Protocol (8) | Header Checksum (16) |
| Source IP (32) |
| Destination IP (32) |
| Options & Padding (32) |
```

## IPv6 Header Format (Base Header = 40 bytes)

```
| VER (4) | Priority/Traffic Class (8) | Flow Label (20) |
| Payload Length (16) | Next Header (8) | Hop Limit (8) |
| Source IP (128) |
| Destination IP (128) |
```

---

## ARP & RARP

- **ARP (Address Resolution Protocol):** Maps IP → MAC address (used in LAN)
- **RARP (Reverse ARP):** Maps MAC → IP

---

*Source: CS Fundamentals(Lets Code) — Computer Network Notes for Placements and GATE*
