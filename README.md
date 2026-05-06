# Transcritor de Áudio em Lote · Aliare

Transcrição local de áudio em português brasileiro usando **faster-whisper** (Whisper otimizado).
Coloque arquivos na pasta `entrada/`, rode o `.bat`, receba `.txt` na pasta `saida/`.

## Pré-requisitos

- **Windows 10 ou 11**
- **Python 3.9+** instalado e no PATH ([download](https://www.python.org/downloads/))
- **Internet na primeira execução** (baixa o modelo do Hugging Face)
- **RAM mínima:**
  - Modelo `small`: 4 GB livres
  - Modelo `medium`: 6 GB livres
  - Modelo `large-v3`: 8 GB livres (recomendado 16 GB)

## Instalação (uma vez só)

1. Extrai todos os arquivos para uma pasta (ex: `C:\Users\paulo.machado\Documents\transcritor-aliare\`)
2. Duplo-clique em **`instalar.bat`**
3. Aguarda — vai baixar ~500MB de dependências (faster-whisper, ctranslate2, tokenizers, etc.)
4. Pronto.

## Uso diário

1. Coloque arquivos de áudio na pasta **`entrada/`**
   - Aceita: `.ogg`, `.mp3`, `.wav`, `.m4a`, `.webm`, `.flac`, `.aac`, `.opus`
2. Duplo-clique em **`transcrever.bat`** (usa modelo `large-v3`, qualidade máxima)
3. Aguarda. Na **primeira execução**, baixa o modelo (~3GB para `large-v3`).
4. Os `.txt` aparecem na pasta **`saida/`** com o mesmo nome do áudio original.

### Variantes prontas

- **`transcrever.bat`** — modelo `large-v3` (~3GB) · qualidade máxima · default
- **`transcrever-medium.bat`** — modelo `medium` (~1.5GB) · 2x mais rápido · qualidade ainda muito boa
- **`transcrever-small.bat`** — modelo `small` (~500MB) · 4x mais rápido · qualidade aceitável

Use o que cabe na sua máquina. Se o `large-v3` estiver muito lento ou estourar memória, desce para `medium`.

## Diferença de qualidade vs. Whisper "tiny" do browser

| Modelo | Tamanho | WER em PT-BR* | Velocidade (CPU) |
|--------|---------|---------------|------------------|
| tiny | 75 MB | ~30-40% | ~5x tempo real |
| base | 150 MB | ~20-25% | ~3x tempo real |
| small | 500 MB | ~10-15% | ~1.5x tempo real |
| medium | 1.5 GB | ~6-8% | ~1x tempo real |
| **large-v3** | **3 GB** | **~4-5%** | **~0.5x tempo real** |

\* Word Error Rate aproximado em áudios brasileiros típicos (reuniões, áudios WhatsApp).

A diferença entre `tiny` e `large-v3` em português brasileiro é categórica — não incremental.

## Aceleração com GPU (opcional)

Se você tem uma GPU NVIDIA com CUDA instalado, o script detecta automaticamente e usa.
Ganho típico: **10x mais rápido**. Áudio de 1h em ~6 minutos.

Para forçar CPU mesmo com GPU presente:
```
set WHISPER_DEVICE=cpu
transcrever.bat
```

## Customização

As variáveis de ambiente abaixo controlam o comportamento:

| Variável | Default | Opções |
|----------|---------|--------|
| `WHISPER_MODEL` | `large-v3` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_LANG` | `pt` | `pt`, `en`, `es`, etc. (ou vazio para auto-detectar) |
| `WHISPER_DEVICE` | `auto` | `cpu`, `cuda`, `auto` |
| `WHISPER_COMPUTE` | `auto` | `int8`, `float16`, `float32`, `auto` |

Exemplo de uso manual:
```
set WHISPER_MODEL=medium
set WHISPER_LANG=pt
transcrever.bat
```

## Como funciona (resumo técnico)

1. **`faster-whisper`** carrega o modelo Whisper em formato CTranslate2 (4x mais rápido que PyTorch)
2. Para cada áudio na pasta `entrada/`:
   - Decodifica via FFmpeg (suporta qualquer codec)
   - Aplica VAD (Voice Activity Detection) para remover silêncios
   - Transcreve em chunks de 30s com beam search (beam_size=5)
   - Aplica fallback ladder de temperatura para combater alucinações
   - Junta segmentos no texto final
3. Salva como `.txt` UTF-8 com mesmo nome do áudio
4. Pula arquivos já transcritos (idempotência)

## Parâmetros anti-alucinação para PT-BR

O script usa parâmetros tunados especificamente para combater o problema clássico
do Whisper em português (loops repetitivos, "alucinação" de frases inventadas):

- `condition_on_previous_text=False` — evita o modelo se "amarrar" em loops
- `compression_ratio_threshold=2.4` — rejeita transcrições com compressão alta (sintoma de loop)
- `log_prob_threshold=-1.0` — descarta segmentos de baixa confiança
- `no_speech_threshold=0.6` — detecta corretamente trechos de silêncio
- `vad_filter=True` — pré-filtra áudio com Silero VAD
- `temperature=[0, 0.2, 0.4, 0.6, 0.8, 1.0]` — fallback progressivo

Estes parâmetros são o motivo da diferença gritante de qualidade comparado à versão browser.

## Troubleshooting

**"Python nao encontrado"**
Instale Python 3.9+ do site oficial e marque "Add Python to PATH".

**"Falha ao criar venv"**
Verifique que tem permissão de escrita na pasta. Se a pasta está em `Downloads`,
mova para `Documents`.

**"OutOfMemoryError" / processo morto silenciosamente**
Modelo grande demais para sua RAM. Use `transcrever-medium.bat` ou `transcrever-small.bat`.

**"Failed to download from Hugging Face"**
Firewall corporativo bloqueando. Solicite ao TI liberação de `huggingface.co`.

**Transcrição muito lenta**
- CPU only é normalmente lento em `large-v3`. Use `medium` ou `small`.
- Se tem GPU NVIDIA, instale CUDA e cuDNN para ativar aceleração.

**Acentuação errada / palavras inventadas**
Sinais de áudio de baixa qualidade. Tente:
- Modelo maior (suba para `large-v3`)
- Pré-processar áudio (normalização de volume, redução de ruído)

---

**Stack:** faster-whisper + CTranslate2 + Silero VAD
**Privacidade:** áudio nunca sai da máquina. Apenas o modelo é baixado uma vez.
**Licença:** livre.

Goiânia, Brasil · 2026
