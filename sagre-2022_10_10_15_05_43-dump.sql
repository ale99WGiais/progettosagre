--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE ONLY public.token DROP CONSTRAINT token_pkey;
ALTER TABLE ONLY public.reparti DROP CONSTRAINT reparti_pk;
ALTER TABLE ONLY public.prodotti DROP CONSTRAINT prodotti_pkey;
ALTER TABLE ONLY public.casse DROP CONSTRAINT casse_pkey;
ALTER TABLE ONLY public.auth DROP CONSTRAINT auth_pkey;
DROP TABLE public.token;
DROP SEQUENCE public.sequence_progressivo;
DROP TABLE public.reparti;
DROP TABLE public.prodotti;
DROP TABLE public.ordini;
DROP TABLE public.coda_stampa;
DROP TABLE public.casse;
DROP TABLE public.auth;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth (
    email text NOT NULL,
    password text,
    operator boolean,
    cms boolean
);


ALTER TABLE public.auth OWNER TO postgres;

--
-- Name: casse; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.casse (
    cassa text NOT NULL,
    ip_stampante text,
    cucina text NOT NULL
);


ALTER TABLE public.casse OWNER TO postgres;

--
-- Name: coda_stampa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coda_stampa (
    ip_stampante text,
    ordine text,
    cmd text,
    time_created timestamp without time zone,
    time_last_printed timestamp without time zone
);


ALTER TABLE public.coda_stampa OWNER TO postgres;

--
-- Name: ordini; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ordini (
    ordine text NOT NULL,
    progressivo integer NOT NULL,
    reparto text NOT NULL,
    prodotto text NOT NULL,
    quantita integer NOT NULL,
    stato text NOT NULL,
    note text,
    cassa text NOT NULL,
    tavolo text NOT NULL,
    cucina text NOT NULL,
    "time" timestamp without time zone NOT NULL,
    annullato boolean DEFAULT false NOT NULL,
    prezzo_unitario numeric(10,2),
    prezzo_totale numeric(10,2),
    cauzione_unitaria numeric(10,2),
    sezione_menu text,
    cauzione_totale numeric(10,2) DEFAULT 0.0 NOT NULL,
    stato_iniziale text NOT NULL
);


ALTER TABLE public.ordini OWNER TO postgres;

--
-- Name: prodotti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prodotti (
    prodotto text NOT NULL,
    quantita_disponibile integer,
    reparto text NOT NULL,
    stato_iniziale text NOT NULL,
    allergeni text,
    prezzo_unitario numeric(10,2) NOT NULL,
    cauzione_unitaria numeric(10,2) DEFAULT 0.0,
    sezione_menu text,
    logo text
);


ALTER TABLE public.prodotti OWNER TO postgres;

--
-- Name: reparti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reparti (
    reparto text NOT NULL,
    stampa_reparto boolean,
    cucina text NOT NULL,
    ip_stampante text,
    logo text
);


ALTER TABLE public.reparti OWNER TO postgres;

--
-- Name: sequence_progressivo; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sequence_progressivo
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sequence_progressivo OWNER TO postgres;

--
-- Name: token; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.token (
    token text NOT NULL,
    email text,
    cucina text,
    cassa text,
    reparto text
);


ALTER TABLE public.token OWNER TO postgres;

--
-- Data for Name: auth; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.auth VALUES ('ale', 'ale', true, true);


--
-- Data for Name: casse; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.casse VALUES ('cassa1', '192.168.1.100', 'cucina1');


--
-- Data for Name: coda_stampa; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: ordini; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.ordini VALUES ('2022-10-09T20:29:14_15', 15, 'cibo', 'Grigliata Mista Carne', 3, 'in lavorazione', 'no pane', 'cassa1', 'A25', 'cucina1', '2022-10-09 20:29:14', true, 14.00, 42.00, 5.00, 'secondi', 15.00, 'generato');
INSERT INTO public.ordini VALUES ('2022-10-09T20:56:33_16', 16, 'bibite', 'Coca Cola', 2, 'chiuso', NULL, 'cassa1', 'A25', 'cucina1', '2022-10-09 20:56:33', false, 2.50, 5.00, 0.00, 'bibite', 0.00, 'chiuso');
INSERT INTO public.ordini VALUES ('2022-10-09T20:29:14_15', 15, 'bibite', 'Coca Cola', 2, 'chiuso', NULL, 'cassa1', 'A25', 'cucina1', '2022-10-09 20:29:14', true, 2.50, 5.00, 0.00, 'bibite', 0.00, 'chiuso');
INSERT INTO public.ordini VALUES ('2022-10-09T20:56:33_16', 16, 'cibo', 'Grigliata Mista Carne', 3, 'in consegna', 'no pane', 'cassa1', 'A25', 'cucina1', '2022-10-09 20:56:33', false, 14.00, 42.00, 5.00, 'secondi', 15.00, 'generato');
INSERT INTO public.ordini VALUES ('2022-10-09T21:21:38_18', 18, 'cibo', 'Grigliata Mista Carne', 3, 'generato', 'no pane', 'cassa1', 'A25', 'cucina1', '2022-10-09 21:21:38', false, 14.00, 42.00, 5.00, 'secondi', 15.00, 'generato');
INSERT INTO public.ordini VALUES ('2022-10-09T21:17:11_17', 17, 'bibite', 'Coca Cola', 1, 'chiuso', NULL, 'cassa1', 'A25', 'cucina1', '2022-10-09 21:17:11', false, 2.50, 2.50, 0.00, 'bibite', 0.00, 'chiuso');
INSERT INTO public.ordini VALUES ('2022-10-09T21:17:11_17', 17, 'cibo', 'Grigliata Mista Carne', 1, 'generato', 'no pane', 'cassa1', 'A25', 'cucina1', '2022-10-09 21:17:11', false, 14.00, 14.00, 5.00, 'secondi', 5.00, 'generato');
INSERT INTO public.ordini VALUES ('2022-10-09T21:21:38_18', 18, 'bibite', 'Coca Cola', 2, 'chiuso', NULL, 'cassa1', 'A25', 'cucina1', '2022-10-09 21:21:38', false, 2.50, 5.00, 0.00, 'bibite', 0.00, 'chiuso');


--
-- Data for Name: prodotti; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.prodotti VALUES ('Grigliata Mista Carne', NULL, 'cibo', 'generato', 'glutine', 14.00, 5.00, 'secondi', 'carne.jpg');
INSERT INTO public.prodotti VALUES ('Coca Cola', 100, 'bibite', 'chiuso', NULL, 2.50, 0.00, 'bibite', 'bibita.jpg');


--
-- Data for Name: reparti; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.reparti VALUES ('cibo', true, 'cucina1', '192.168.1.100', NULL);
INSERT INTO public.reparti VALUES ('bibite', false, 'cucina1', NULL, NULL);


--
-- Data for Name: token; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.token VALUES ('aleIvaQEFOJPB_gbraLmUk5zMhFQA5xIZt3Ts4hfjdTOoo', 'ale', 'cucina1', NULL, 'cibo');
INSERT INTO public.token VALUES ('ale1dW8pJ5vPP0V1jzqOtOEhW3ArCjOwSwwdiwwiNPjgak', 'ale', 'cucina1', 'cassa1', NULL);
INSERT INTO public.token VALUES ('alefDUTHLGJ9ImKGkVO1-o-etFCuHN2ptMbjNDxWQJvOJ8', 'ale', NULL, NULL, NULL);


--
-- Name: sequence_progressivo; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sequence_progressivo', 18, true);


--
-- Name: auth auth_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth
    ADD CONSTRAINT auth_pkey PRIMARY KEY (email);


--
-- Name: casse casse_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.casse
    ADD CONSTRAINT casse_pkey PRIMARY KEY (cassa);


--
-- Name: prodotti prodotti_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prodotti
    ADD CONSTRAINT prodotti_pkey PRIMARY KEY (prodotto);


--
-- Name: reparti reparti_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reparti
    ADD CONSTRAINT reparti_pk PRIMARY KEY (cucina, reparto);


--
-- Name: token token_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.token
    ADD CONSTRAINT token_pkey PRIMARY KEY (token);


--
-- PostgreSQL database dump complete
--

