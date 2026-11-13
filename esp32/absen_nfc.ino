#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* URL_DASAR = "https://41e8120c54c6e7.lhr.life";

const int PIN_LED_HIJAU = 26;
const int PIN_LED_MERAH = 33;
const int PIN_PINTU = 32;
const int PIN_BUZZER = 13;

MFRC522 rfid(5, 21);

void sambungWifi() {
  Serial.print("Menyambung Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  int percobaan = 0;
  while (WiFi.status() != WL_CONNECTED && percobaan < 20) {
    delay(500);
    Serial.print(".");
    percobaan++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi tersambung, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi gagal");
  }
}

// Hasil: 1 = diizinkan, 0 = ditolak, -1 = server tidak terjangkau
int tanyaServer(String uid, String &nama) {
  nama = "-";
  if (WiFi.status() != WL_CONNECTED) {
    return -1;
  }
  HTTPClient http;
  http.begin(String(URL_DASAR) + "/tap");
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  int kode = http.POST("{\"uid\":\"" + uid + "\"}");
  Serial.print("Balasan server, kode: ");
  Serial.println(kode);
  if (kode != 200) {
    http.end();
    return -1;
  }
  String isi = http.getString();
  http.end();

  int awal = isi.indexOf("\"nama\":\"");
  if (awal >= 0) {
    awal += 8;
    int akhir = isi.indexOf("\"", awal);
    nama = isi.substring(awal, akhir);
  }
  if (isi.indexOf("\"izin\":true") >= 0) {
    return 1;
  }
  return 0;
}

String bacaKartu() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return "";
  }
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  rfid.PICC_HaltA();
  return uid;
}

void bunyi(int frekuensi, int durasiMs) {
  long periode = 1000000L / frekuensi;
  long jumlahSiklus = (long)durasiMs * 1000L / periode;
  for (long i = 0; i < jumlahSiklus; i++) {
    digitalWrite(PIN_BUZZER, HIGH);
    delayMicroseconds(periode / 2);
    digitalWrite(PIN_BUZZER, LOW);
    delayMicroseconds(periode / 2);
  }
}

void bukaPintu() {
  Serial.println("Pintu TERBUKA");
  digitalWrite(PIN_PINTU, HIGH);
  delay(3000);
  digitalWrite(PIN_PINTU, LOW);
  Serial.println("Pintu TERKUNCI");
}

void tolak() {
  digitalWrite(PIN_LED_MERAH, HIGH);
  bunyi(300, 200);
  delay(100);
  bunyi(300, 200);
  delay(1000);
  digitalWrite(PIN_LED_MERAH, LOW);
}

void setup() {
  pinMode(PIN_LED_HIJAU, OUTPUT);
  pinMode(PIN_LED_MERAH, OUTPUT);
  pinMode(PIN_PINTU, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  sambungWifi();
  Serial.println("Siap, tempelkan kartu");
}

void loop() {
  String uid = bacaKartu();

  if (uid == "") {
    delay(50);
    return;
  }

  Serial.print("UID: ");
  Serial.println(uid);

  String nama;
  int hasil = tanyaServer(uid, nama);

  if (hasil == 1) {
    Serial.print("Selamat datang, ");
    Serial.println(nama);
    digitalWrite(PIN_LED_HIJAU, HIGH);
    bunyi(1000, 200);
    bukaPintu();
    digitalWrite(PIN_LED_HIJAU, LOW);
  } else if (hasil == 0) {
    Serial.println("Kartu tidak terdaftar, akses ditolak");
    tolak();
  } else {
    Serial.println("Server tidak terjangkau, akses ditolak");
    tolak();
  }
}
