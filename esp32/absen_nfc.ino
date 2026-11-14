#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// ===== Ganti dua baris ini sebelum dijalankan =====
// Wokwi: alamat tunnel (https://...). Alat asli: alamat lokal server, misalnya http://192.168.1.20:8000
const char* URL_DASAR = "https://GANTI-ALAMAT-TUNNEL";
// Samakan dengan API_KEY di file .env (jangan unggah kunci asli ke GitHub)
const char* API_KEY = "GANTI_KUNCI";

// ===== Wi-Fi =====
const char* WIFI_SSID = "Wokwi-GUEST";  // alat asli: nama Wi-Fi sendiri
const char* WIFI_PASS = "";             // alat asli: sandi Wi-Fi
const int WIFI_KANAL = 6;               // Wokwi: 6 (lebih cepat). Alat asli: 0 (otomatis)

const int PIN_LED_HIJAU = 26;
const int PIN_LED_MERAH = 33;
const int PIN_PINTU = 32;
const int PIN_BUZZER = 13;

MFRC522 rfid(5, 21);

// Menyambung Wi-Fi; di tengah waktu tunggu, konfigurasi dibersihkan lalu dicoba lagi
bool sambungWifi(int detikMaks) {
  Serial.print("Menyambung Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASS, WIFI_KANAL);
  for (int i = 0; i < detikMaks * 2 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
    if (i == detikMaks) {
      WiFi.disconnect(true);
      WiFi.begin(WIFI_SSID, WIFI_PASS, WIFI_KANAL);
    }
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi tersambung, IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }
  Serial.print("Wi-Fi gagal, kode status: ");
  Serial.println(WiFi.status());
  return false;
}

// Hasil: 1 = diizinkan, 0 = ditolak, -1 = server tidak terjangkau, -2 = kunci API salah
int tanyaServer(String uid, String &nama) {
  nama = "-";
  if (WiFi.status() != WL_CONNECTED && !sambungWifi(15)) {
    return -1;
  }

  WiFiClientSecure klienAman;
  WiFiClient klienBiasa;
  HTTPClient http;
  String url = String(URL_DASAR) + "/tap";
  bool mulai;
  if (url.startsWith("https://")) {
    klienAman.setInsecure();  // simulasi: sertifikat tunnel tidak diperiksa
    mulai = http.begin(klienAman, url);
  } else {
    mulai = http.begin(klienBiasa, url);
  }
  if (!mulai) {
    Serial.println("Alamat server tidak valid");
    return -1;
  }
  http.setTimeout(10000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);

  int kode = http.POST("{\"uid\":\"" + uid + "\"}");
  Serial.print("Balasan server, kode: ");
  Serial.println(kode);
  if (kode < 0) {
    Serial.println(HTTPClient::errorToString(kode));
    http.end();
    return -1;
  }
  if (kode == 401) {
    http.end();
    return -2;
  }
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
  rfid.PCD_StopCrypto1();
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
  sambungWifi(30);
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
  } else if (hasil == -2) {
    Serial.println("Kunci API salah, samakan API_KEY dengan file .env");
    tolak();
  } else {
    Serial.println("Server tidak terjangkau, akses ditolak");
    tolak();
  }
}
