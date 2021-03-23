-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2021-03-23 07:37:43
-- 服务器版本： 10.1.38-MariaDB
-- PHP 版本： 7.3.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `mei`
--
CREATE DATABASE IF NOT EXISTS `mei` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `mei`;

-- --------------------------------------------------------

--
-- 表的结构 `armor_id`
--

CREATE TABLE `armor_id` (
  `id` int(11) NOT NULL,
  `attack` int(11) NOT NULL,
  `defense` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `armor_id`
--

INSERT INTO `armor_id` (`id`, `attack`, `defense`) VALUES
(1, 1, 0),
(2, 0, 1),
(3, 0, 1),
(4, 0, 1),
(5, 0, 1),
(7, 1024, 1024),
(8, 3, 0),
(9, 999, 0);

-- --------------------------------------------------------

--
-- 表的结构 `attribute`
--

CREATE TABLE `attribute` (
  `qq` char(10) NOT NULL,
  `experience` int(11) NOT NULL DEFAULT '0',
  `point` int(11) NOT NULL DEFAULT '0',
  `hp` int(11) NOT NULL DEFAULT '100',
  `max_hp` int(11) NOT NULL DEFAULT '100',
  `attack` int(11) NOT NULL DEFAULT '1',
  `defense` int(11) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `ban`
--

CREATE TABLE `ban` (
  `qq` char(10) NOT NULL,
  `count` int(11) NOT NULL DEFAULT '10',
  `date` date NOT NULL DEFAULT '0000-00-00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `buff_id`
--

CREATE TABLE `buff_id` (
  `buff` int(11) NOT NULL,
  `name` varchar(32) NOT NULL,
  `info` varchar(32) NOT NULL,
  `attack` int(11) NOT NULL,
  `defense` int(11) NOT NULL,
  `hp_max` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `buff_id`
--

INSERT INTO `buff_id` (`buff`, `name`, `info`, `attack`, `defense`, `hp_max`) VALUES
(1, '神龟', '增加20点防御，减少40点攻击。', -40, 20, 0),
(2, '狂暴', '增加10点攻击，减少20点防御', 10, -20, 0);

-- --------------------------------------------------------

--
-- 表的结构 `effect`
--

CREATE TABLE `effect` (
  `qq` int(11) NOT NULL,
  `buff` int(11) NOT NULL,
  `time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `equipment`
--

CREATE TABLE `equipment` (
  `qq` char(10) NOT NULL,
  `type` tinyint(4) NOT NULL,
  `id` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `info`
--

CREATE TABLE `info` (
  `qq` char(10) NOT NULL,
  `coin` bigint(11) NOT NULL DEFAULT '0',
  `date` date NOT NULL DEFAULT '0000-00-00',
  `stamina` int(11) NOT NULL DEFAULT '200',
  `chip` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `inventory`
--

CREATE TABLE `inventory` (
  `qq` char(10) NOT NULL,
  `id` int(11) NOT NULL,
  `count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `item_id`
--

CREATE TABLE `item_id` (
  `id` int(11) NOT NULL,
  `name` varchar(32) NOT NULL,
  `type` tinyint(4) NOT NULL DEFAULT '0',
  `info` varchar(256) NOT NULL,
  `nbt` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `item_id`
--

INSERT INTO `item_id` (`id`, `name`, `type`, `info`, `nbt`) VALUES
(0, '空', 0, '', ''),
(1, '木剑', 2, '普通的木剑，装备可增加1点攻击', ''),
(2, '布帽', 4, '普通的布帽，装备可增加1点防御', ''),
(3, '布甲', 5, '普通的布甲，装备可增加1点防御', ''),
(4, '棉裤', 6, '普通的棉裤，装备可增加1点防御', ''),
(5, '布鞋', 7, '普通的布鞋，装备可增加1点防御', ''),
(6, '布套装', 1, '使用可获得 布帽、布甲、棉裤、布鞋 各一件', '[user.give(i,1) for i in range(2,6)]'),
(7, '魔戒', 8, '', ''),
(8, '石剑', 2, '普通的石剑，装备可增加3点攻击', ''),
(9, '屠龙宝刀', 2, '一刀999！！！', ''),
(10, '神龟药水（10分钟）', 1, '使用后获得10分钟神龟效果（防御增加20，攻击减少40）', 'user.add_buff(1,60*10)'),
(11, '神龟药水（1小时）', 1, '使用后获得1小时神龟效果（防御增加20，攻击减少40）。', 'user.add_buff(1,60*60)'),
(12, '解毒剂', 1, '使用可解除所有状态', 'user.sub_buff()'),
(13, '狂暴药水', 1, '使用后获得1分钟的狂暴效果（攻击增加10，防御降低20）', 'user.add_buff(2,60)'),
(14, '芽衣妹汁', 1, '使用后获得30体力', 'user.gain(30,\'stamina\')');

-- --------------------------------------------------------

--
-- 表的结构 `shop`
--

CREATE TABLE `shop` (
  `priority` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `sell` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `shop`
--

INSERT INTO `shop` (`priority`, `id`, `price`, `sell`) VALUES
(0, 1, 3, 2),
(0, 2, 3, 2),
(0, 3, 3, 2),
(0, 4, 3, 2),
(0, 5, 3, 2),
(1, 6, 12, 8),
(1, 8, 20, 10),
(9, 9, 999999, -1),
(0, 10, 20, 14),
(1, 11, 100, 70),
(1, 12, 10, 7),
(1, 13, 100, 60),
(1, 14, 100, 50);

-- --------------------------------------------------------

--
-- 表的结构 `type_id`
--

CREATE TABLE `type_id` (
  `type` tinyint(4) NOT NULL,
  `info` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `type_id`
--

INSERT INTO `type_id` (`type`, `info`) VALUES
(0, '普通物品'),
(1, '可使用'),
(2, '主手'),
(3, '副手'),
(4, '头'),
(5, '胸'),
(6, '腿'),
(7, '脚'),
(8, '饰品');

--
-- 转储表的索引
--

--
-- 表的索引 `armor_id`
--
ALTER TABLE `armor_id`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `attribute`
--
ALTER TABLE `attribute`
  ADD PRIMARY KEY (`qq`);

--
-- 表的索引 `ban`
--
ALTER TABLE `ban`
  ADD PRIMARY KEY (`qq`);

--
-- 表的索引 `buff_id`
--
ALTER TABLE `buff_id`
  ADD PRIMARY KEY (`buff`);

--
-- 表的索引 `effect`
--
ALTER TABLE `effect`
  ADD PRIMARY KEY (`qq`,`buff`);

--
-- 表的索引 `equipment`
--
ALTER TABLE `equipment`
  ADD PRIMARY KEY (`qq`,`type`);

--
-- 表的索引 `info`
--
ALTER TABLE `info`
  ADD PRIMARY KEY (`qq`);

--
-- 表的索引 `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`qq`,`id`);

--
-- 表的索引 `item_id`
--
ALTER TABLE `item_id`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `shop`
--
ALTER TABLE `shop`
  ADD PRIMARY KEY (`id`),
  ADD KEY `priority` (`priority`);

--
-- 表的索引 `type_id`
--
ALTER TABLE `type_id`
  ADD PRIMARY KEY (`type`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
