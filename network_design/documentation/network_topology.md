# Campus Network Topology

## Overview

The network represents a VIT Vellore-inspired smart-campus communication system. It contains separate network zones for academic users, administration, hostel users, IoT devices, and application servers.

## Network Zones

1. Academic Zone
2. Administration Zone
3. Hostel/User Zone
4. IoT/Lab Zone
5. Server Zone

## Main Devices

- Core router
- Academic switch
- Administration switch
- Hostel/User switch
- IoT/Lab switch
- DNS/Application server
- Client computers

## Communication Flow

A client in the Academic Zone sends a request to the Application Server in the Server Zone. The request passes through the local switch, core router, and server-side switch.

DNS is used to resolve the hostname:

campus-app.local

The resolved address is:

192.168.50.10

## Purpose

The topology will be used to demonstrate:

- IP addressing
- Subnetting
- Routing
- DNS resolution
- Packet movement
- Communication between different network segments