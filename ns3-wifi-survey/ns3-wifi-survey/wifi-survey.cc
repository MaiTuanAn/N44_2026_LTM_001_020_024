/*
 * Đề tài: Khảo sát ảnh hưởng của số lượng thiết bị và khoảng cách đến hiệu năng mạng Wi-Fi bằng ns-3
 * Tệp nguồn: scratch/wifi-survey.cc
 * Tương thích: ns-3.36+ đến ns-3.42+ (CMake ./ns3 CLI)
 */

#include "ns3/applications-module.h"
#include "ns3/command-line.h"
#include "ns3/config.h"
#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/ssid.h"
#include "ns3/wifi-module.h"
#include "ns3/yans-wifi-helper.h"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("WifiSurveySimulation");

int
main(int argc, char* argv[])
{
    // 1. Khai báo tham số cấu hình mặc định (Command Line Parameters)
    uint32_t nSta = 10;                  // Số lượng trạm (STA) kết nối vào AP
    double distance = 20.0;              // Khoảng cách từ các STA đến AP (m)
    double simTime = 15.0;               // Thời gian mô phỏng (s)
    uint32_t payloadSize = 1472;         // Kích thước gói tin (Byte)
    std::string dataRate = "20Mbps";     // Tốc độ gửi ứng dụng trên mỗi STA
    std::string protocol = "UDP";        // Giao thức tầng giao vận: "UDP" hoặc "TCP"
    bool enableRtsCts = false;           // Bật/tắt cơ chế RTS/CTS
    uint32_t seed = 1;                   // Run seed cho thống kê ngẫu nhiên
    std::string csvFile = "results.csv"; // Tệp xuất dữ liệu thống kê

    CommandLine cmd(__FILE__);
    cmd.AddValue("nSta", "Số lượng thiết bị trạm Wi-Fi (STA)", nSta);
    cmd.AddValue("distance", "Khoảng cách từ STA đến AP (mét)", distance);
    cmd.AddValue("simTime", "Thời gian mô phỏng (giây)", simTime);
    cmd.AddValue("payloadSize", "Kích thước payload gói tin (bytes)", payloadSize);
    cmd.AddValue("dataRate", "Tốc độ tạo lưu lượng mỗi trạm (ví dụ: 10Mbps, 20Mbps)", dataRate);
    cmd.AddValue("protocol", "Giao thức truyền tải (UDP hoặc TCP)", protocol);
    cmd.AddValue("enableRtsCts", "Bật cơ chế bảo vệ RTS/CTS (true/false)", enableRtsCts);
    cmd.AddValue("seed", "Giá trị RngRun phục vụ chạy lặp lấy trung bình", seed);
    cmd.AddValue("csvFile", "Đường dẫn file CSV lưu kết quả", csvFile);
    cmd.Parse(argc, argv);

    // Thiết lập hạt giống ngẫu nhiên (Random Seed)
    RngSeedManager::SetSeed(12345);
    RngSeedManager::SetRun(seed);

    // Cấu hình ngưỡng RTS/CTS
    UintegerValue ctsThr = (enableRtsCts ? UintegerValue(100) : UintegerValue(65535));
    Config::SetDefault("ns3::WifiRemoteStationManager::RtsCtsThreshold", ctsThr);
    Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue(payloadSize));

    // 2. Khởi tạo các nút mạng (Nodes): 1 AP và nSta thiết bị đầu cuối
    NodeContainer wifiApNode;
    wifiApNode.Create(1);
    NodeContainer wifiStaNodes;
    wifiStaNodes.Create(nSta);

    // 3. Thiết lập kênh truyền vật lý (YansWifiChannel & LogDistancePropagationLossModel)
    YansWifiChannelHelper channel;
    channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
                               "Exponent", DoubleValue(3.0),
                               "ReferenceDistance", DoubleValue(1.0),
                               "ReferenceLoss", DoubleValue(46.6777));

    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());
    phy.Set("TxPowerStart", DoubleValue(20.0)); // Công suất phát 20 dBm
    phy.Set("TxPowerEnd", DoubleValue(20.0));

    // 4. Cấu hình chuẩn Wi-Fi (IEEE 802.11ax / 802.11ac) và điều khiển tốc độ MinstrelHt
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211ax);
    wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");

    WifiMacHelper mac;
    Ssid ssid = Ssid("ns3-wifi-survey");

    // Cài đặt NetDevice cho các trạm STA
    mac.SetType("ns3::StaWifiMac",
                "Ssid", SsidValue(ssid),
                "ActiveProbing", BooleanValue(false));
    NetDeviceContainer staDevices = wifi.Install(phy, mac, wifiStaNodes);

    // Cài đặt NetDevice cho trạm thu phát AP
    mac.SetType("ns3::ApWifiMac",
                "Ssid", SsidValue(ssid));
    NetDeviceContainer apDevice = wifi.Install(phy, mac, wifiApNode);

    // 5. Thiết lập mô hình vị trí (Mobility Model)
    // Đặt AP tại tâm (0, 0, 0) và phân bố đều các STA trên đường tròn bán kính `distance`
    MobilityHelper mobility;
    Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator>();
    positionAlloc->Add(Vector(0.0, 0.0, 0.0)); // Vị trí của AP

    for (uint32_t i = 0; i < nSta; ++i)
    {
        double angle = 2.0 * M_PI * i / nSta;
        double x = distance * std::cos(angle);
        double y = distance * std::sin(angle);
        positionAlloc->Add(Vector(x, y, 0.0));
    }

    mobility.SetPositionAllocator(positionAlloc);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(wifiApNode);
    mobility.Install(wifiStaNodes);

    // 6. Cài đặt chồng giao thức Internet (TCP/IPv4)
    InternetStackHelper stack;
    stack.Install(wifiApNode);
    stack.Install(wifiStaNodes);

    Ipv4AddressHelper address;
    address.SetBase("192.168.1.0", "255.255.255.0");
    Ipv4InterfaceContainer apInterface = address.Assign(apDevice);
    Ipv4InterfaceContainer staInterfaces = address.Assign(staDevices);

    // 7. Cài đặt ứng dụng sinh lưu lượng (Uplink: STA -> AP)
    uint16_t basePort = 5000;
    ApplicationContainer serverApps;
    ApplicationContainer clientApps;

    std::string socketFactory = (protocol == "TCP") ? "ns3::TcpSocketFactory" : "ns3::UdpSocketFactory";

    for (uint32_t i = 0; i < nSta; ++i)
    {
        uint16_t port = basePort + i;

        // Cài đặt PacketSink trên AP để thu nhận gói tin từ STA thứ i
        PacketSinkHelper sinkHelper(socketFactory, InetSocketAddress(Ipv4Address::GetAny(), port));
        serverApps.Add(sinkHelper.Install(wifiApNode.Get(0)));

        // Cài đặt OnOffApplication (CBR) trên từng STA hướng về AP
        OnOffHelper clientHelper(socketFactory, InetSocketAddress(apInterface.GetAddress(0), port));
        clientHelper.SetAttribute("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=1]"));
        clientHelper.SetAttribute("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0]"));
        clientHelper.SetAttribute("PacketSize", UintegerValue(payloadSize));
        clientHelper.SetAttribute("DataRate", DataRateValue(DataRate(dataRate)));

        ApplicationContainer app = clientHelper.Install(wifiStaNodes.Get(i));
        // Khởi động lệch pha nhẹ (jitter) từ 1.0s đến 1.1s để tránh đồng bộ hóa gói ARP đầu tiên
        double startOffset = 1.0 + (0.1 * i / std::max(1u, nSta));
        app.Start(Seconds(startOffset));
        app.Stop(Seconds(simTime));
        clientApps.Add(app);
    }

    serverApps.Start(Seconds(0.5));
    serverApps.Stop(Seconds(simTime + 0.5));

    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    // 8. Kích hoạt FlowMonitor để đo lường các chỉ số QoS
    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();

    Simulator::Stop(Seconds(simTime + 1.0));
    Simulator::Run();

    // 9. Trích xuất và tính toán số liệu từ FlowMonitor
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats();

    double totalThroughputMbps = 0.0;
    double sumThroughputSq = 0.0;
    double totalDelayMs = 0.0;
    double totalJitterMs = 0.0;
    uint64_t totalTxPackets = 0;
    uint64_t totalRxPackets = 0;
    uint32_t countedFlows = 0;

    double activeTime = simTime - 1.0; // Thời gian truyền thực tế

    for (auto const& [flowId, flowStats] : stats)
    {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(flowId);

        // Chỉ thống kê các luồng dữ liệu chiều lên (từ STA gửi tới địa chỉ IP của AP)
        if (t.destinationAddress == apInterface.GetAddress(0) && t.destinationPort >= basePort)
        {
            double flowThrMbps = (flowStats.rxBytes * 8.0) / (activeTime * 1e6);
            totalThroughputMbps += flowThrMbps;
            sumThroughputSq += (flowThrMbps * flowThrMbps);

            totalTxPackets += flowStats.txPackets;
            totalRxPackets += flowStats.rxPackets;

            if (flowStats.rxPackets > 0)
            {
                totalDelayMs += (flowStats.delaySum.GetSeconds() / flowStats.rxPackets) * 1000.0;
            }
            if (flowStats.rxPackets > 1)
            {
                totalJitterMs += (flowStats.jitterSum.GetSeconds() / (flowStats.rxPackets - 1)) * 1000.0;
            }
            countedFlows++;
        }
    }

    double avgDelayMs = (countedFlows > 0) ? (totalDelayMs / countedFlows) : 0.0;
    double avgJitterMs = (countedFlows > 0) ? (totalJitterMs / countedFlows) : 0.0;
    double packetLossRatio = (totalTxPackets > 0)
                                 ? (static_cast<double>(totalTxPackets - totalRxPackets) / totalTxPackets) * 100.0
                                 : 0.0;
    double jainsFairness = (countedFlows > 0 && sumThroughputSq > 0.0)
                               ? (totalThroughputMbps * totalThroughputMbps) / (countedFlows * sumThroughputSq)
                               : 0.0;
    double perStaThroughputMbps = (nSta > 0) ? (totalThroughputMbps / nSta) : 0.0;

    // Hiển thị tóm tắt ra màn hình console
    std::cout << std::fixed << std::setprecision(3)
              << "[DONE] nSta=" << nSta
              << " | dist=" << distance << "m"
              << " | proto=" << protocol
              << " | RTS/CTS=" << (enableRtsCts ? "ON" : "OFF")
              << " --> TotalThr=" << totalThroughputMbps << " Mbps"
              << " | AvgDelay=" << avgDelayMs << " ms"
              << " | Loss=" << packetLossRatio << " %"
              << " | Fairness=" << jainsFairness << std::endl;

    // 10. Ghi kết quả nối tiếp vào file CSV
    bool writeHeader = false;
    std::ifstream checkFile(csvFile);
    if (!checkFile.good() || checkFile.peek() == std::ifstream::traits_type::eof())
    {
        writeHeader = true;
    }
    checkFile.close();

    std::ofstream out(csvFile, std::ios::app);
    if (writeHeader)
    {
        out << "nSta,distance,protocol,rtsCts,seed,totalThroughputMbps,perStaThroughputMbps,"
               "avgDelayMs,avgJitterMs,packetLossPct,jainsFairness,txPackets,rxPackets\n";
    }
    out << nSta << ","
        << distance << ","
        << protocol << ","
        << (enableRtsCts ? 1 : 0) << ","
        << seed << ","
        << std::fixed << std::setprecision(4)
        << totalThroughputMbps << ","
        << perStaThroughputMbps << ","
        << avgDelayMs << ","
        << avgJitterMs << ","
        << packetLossRatio << ","
        << jainsFairness << ","
        << totalTxPackets << ","
        << totalRxPackets << "\n";
    out.close();

    Simulator::Destroy();
    return 0;
}