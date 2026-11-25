/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.13-MariaDB, for Linux (aarch64)
--
-- Host: localhost    Database: absen_nfc
-- ------------------------------------------------------
-- Server version	11.4.13-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `absen`
--

DROP TABLE IF EXISTS `absen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `absen` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(20) NOT NULL,
  `npm` varchar(20) DEFAULT NULL,
  `nama` varchar(40) NOT NULL,
  `status` varchar(10) NOT NULL,
  `waktu` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `waktu` (`waktu`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `absen`
--

LOCK TABLES `absen` WRITE;
/*!40000 ALTER TABLE `absen` DISABLE KEYS */;
INSERT INTO `absen` VALUES
(1,'01020304',NULL,'Sandor','diterima','2026-11-12 00:35:13'),
(2,'11223344',NULL,'Leon','diterima','2026-11-12 00:57:45'),
(3,'55667788',NULL,'Rama','diterima','2026-11-12 00:58:35'),
(4,'AABBCCDD',NULL,'-','ditolak','2026-11-12 00:59:45'),
(5,'01020304',NULL,'Sandor','Diterima','2026-11-12 08:12:01'),
(6,'1122334455',NULL,'Leon','Diterima','2026-11-12 08:12:35'),
(7,'11223344',NULL,'Leon','Diterima','2026-11-12 08:13:08'),
(8,'11223344',NULL,'Leon','Diterima','2026-11-12 08:13:30'),
(9,'01020304',NULL,'-','ditolak','2026-11-12 20:57:24'),
(10,'11223344',NULL,'-','ditolak','2026-11-12 20:58:04'),
(11,'55667788',NULL,'-','ditolak','2026-11-12 20:58:25'),
(12,'55667788',NULL,'-','ditolak','2026-11-12 21:02:42'),
(13,'11223344',NULL,'-','ditolak','2026-11-12 21:03:00'),
(14,'01020304',NULL,'-','ditolak','2026-11-12 21:03:18'),
(15,'AABBCCDD',NULL,'-','ditolak','2026-11-12 21:03:40'),
(16,'04112233',NULL,'-','ditolak','2026-11-12 21:04:40'),
(17,'01020304',NULL,'-','ditolak','2026-11-13 05:39:57'),
(18,'01020304',NULL,'-','ditolak','2026-11-13 05:39:59'),
(19,'01020304',NULL,'Sandor','diterima','2026-11-13 05:42:35'),
(20,'01020304',NULL,'Sandor','diterima','2026-11-13 05:46:48'),
(21,'11223344',NULL,'Leon','diterima','2026-11-13 05:47:09'),
(22,'AABBCCDD',NULL,'-','ditolak','2026-11-13 05:47:29'),
(23,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-13 05:48:54'),
(24,'01020304',NULL,'Sandor','diterima','2026-11-13 11:17:50'),
(25,'55667788',NULL,'Rama','diterima','2026-11-13 11:18:09'),
(26,'11223344',NULL,'Leon','diterima','2026-11-13 11:19:00'),
(27,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-13 11:19:21'),
(28,'04112233',NULL,'-','ditolak','2026-11-13 11:19:43'),
(29,'C0FFEE99',NULL,'-','ditolak','2026-11-13 11:19:59'),
(30,'01020304',NULL,'Sandor','diterima','2026-11-13 11:20:18'),
(31,'55667788',NULL,'Rama','diterima','2026-11-13 11:20:37'),
(32,'55667788',NULL,'Rama','diterima','2026-11-13 11:23:33'),
(33,'11223344',NULL,'Leon','diterima','2026-11-13 11:23:59'),
(34,'01020304',NULL,'Sandor','diterima','2026-11-13 11:25:21'),
(35,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-13 11:25:52'),
(36,'55667788',NULL,'Rama','diterima','2026-11-13 11:26:16'),
(37,'04112233',NULL,'-','ditolak','2026-11-13 11:26:38'),
(38,'C0FFEE99',NULL,'-','ditolak','2026-11-13 11:28:31'),
(39,'11223344',NULL,'Leon','diterima','2026-11-13 11:28:52'),
(40,'SANDOR',NULL,'-','ditolak','2026-11-13 16:11:18'),
(41,'DEADBEEF','0000000000','Tes NPM','diterima','2026-11-14 06:48:17'),
(42,'11223344',NULL,'Leon','diterima','2026-11-14 06:56:42'),
(43,'01020304',NULL,'Sandor','diterima','2026-11-14 06:57:52'),
(44,'55667788',NULL,'Rama','diterima','2026-11-14 06:58:09'),
(45,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-14 06:58:34'),
(46,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-14 11:53:38'),
(47,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-14 16:42:36'),
(48,'12345678',NULL,'Nichol','diterima','2026-11-14 17:32:43'),
(49,'11223344',NULL,'Leon','diterima','2026-11-14 17:33:41'),
(50,'01020304',NULL,'Sandor','diterima','2026-11-14 17:35:29'),
(51,'01026389',NULL,'-','ditolak','2026-11-14 17:35:49'),
(52,'AABBCCDD',NULL,'Fahmi','diterima','2026-11-14 18:57:33'),
(53,'12345678',NULL,'Nichol','diterima','2026-11-14 18:58:12'),
(54,'11111111',NULL,'Ria','diterima','2026-11-17 12:42:27'),
(55,'12348765',NULL,'Fani','diterima','2026-11-17 12:43:37');
/*!40000 ALTER TABLE `absen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kartu`
--

DROP TABLE IF EXISTS `kartu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `kartu` (
  `uid` varchar(20) NOT NULL,
  `npm` varchar(20) DEFAULT NULL,
  `nama` varchar(40) NOT NULL,
  `dibuat` datetime NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `npm` (`npm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kartu`
--

LOCK TABLES `kartu` WRITE;
/*!40000 ALTER TABLE `kartu` DISABLE KEYS */;
INSERT INTO `kartu` VALUES
('01020304',NULL,'Sandor','2026-11-13 05:40:39'),
('11111111',NULL,'Ria','2026-11-17 12:42:13'),
('11223344',NULL,'Leon','2026-11-13 05:41:04'),
('12345678',NULL,'Nichol','2026-11-13 16:14:37'),
('12348765',NULL,'Fani','2026-11-17 12:43:15'),
('55667788',NULL,'Rama','2026-11-13 05:41:24'),
('87654321','2513020061','Iqbal','2026-11-14 11:51:17'),
('AABBCCDD',NULL,'Fahmi','2026-11-13 05:48:29');
/*!40000 ALTER TABLE `kartu` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-11-25  8:20:04
