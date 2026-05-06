"""
Transcritor de Áudio em Lote - Aliare
======================================
Lê todos os arquivos de áudio da pasta `entrada/` e gera transcrições .txt
correspondentes na pasta `saida/`.

Suporta: .ogg, .mp3, .wav, .m4a, .webm, .flac, .aac, .opus
"""

import os
import sys
import time
from pathlib import Path

# ===== Configurações =====
PASTA_ENTRADA = "entrada"
PASTA_SAIDA = "saida"
EXTENSOES_VALIDAS = {".ogg", ".mp3", ".wav", ".m4a", ".webm", ".flac", ".aac", ".opus"}

# Tamanho do modelo - você pode trocar via variável de ambiente WHISPER_MODEL
# Opções (do mais rápido ao mais preciso):
#   tiny      ~75MB    - rápido mas impreciso (NÃO recomendo para PT-BR)
#   base      ~150MB   - equilíbrio razoável
#   small     ~500MB   - bom para PT-BR
#   medium    ~1.5GB   - excelente para PT-BR (RECOMENDADO se a CPU aguentar)
#   large-v3  ~3GB     - estado da arte (RECOMENDADO se tiver GPU ou paciência)
MODELO = os.environ.get("WHISPER_MODEL", "large-v3")

# Idioma forçado - "pt" para português brasileiro
IDIOMA = os.environ.get("WHISPER_LANG", "pt")

# Device: "cpu", "cuda" (NVIDIA) ou "auto"
DEVICE = os.environ.get("WHISPER_DEVICE", "auto")

# Compute type: "int8" (CPU, rápido), "float16" (GPU), "float32" (máxima precisão)
COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE", "auto")


def imprimir_cabecalho():
    print()
    print(" " + "=" * 60)
    print("   TRANSCRITOR DE ÁUDIO EM LOTE - Aliare")
    print("   Whisper local · 100% offline após primeiro download")
    print(" " + "=" * 60)
    print()


def detectar_device_e_compute():
    """Detecta GPU NVIDIA disponível e ajusta parâmetros."""
    device = DEVICE
    compute = COMPUTE_TYPE

    if device == "auto":
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                print(f" [INFO] GPU NVIDIA detectada: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
        except ImportError:
            device = "cpu"

    if compute == "auto":
        compute = "float16" if device == "cuda" else "int8"

    print(f" [INFO] Device: {device} · Compute type: {compute}")
    return device, compute


def encontrar_arquivos(pasta_entrada: Path):
    """Lista todos os arquivos de áudio válidos na pasta de entrada."""
    if not pasta_entrada.exists():
        pasta_entrada.mkdir(parents=True, exist_ok=True)
        print(f" [INFO] Pasta '{pasta_entrada}' criada. Coloque seus áudios lá e rode novamente.")
        return []

    arquivos = sorted([
        f for f in pasta_entrada.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSOES_VALIDAS
    ])
    return arquivos


def transcrever_arquivo(model, arquivo: Path, pasta_saida: Path) -> bool:
    """Transcreve um arquivo e salva como .txt. Retorna True em sucesso."""
    arquivo_saida = pasta_saida / (arquivo.stem + ".txt")

    # Pula se já existe (idempotência)
    if arquivo_saida.exists():
        print(f"   [SKIP] Já transcrito: {arquivo_saida.name}")
        return True

    print(f"   [PROC] {arquivo.name} ({arquivo.stat().st_size / 1024 / 1024:.2f} MB)")
    inicio = time.time()

    try:
        # Parâmetros tunados para PT-BR (combatem alucinação/repetição):
        # - language="pt": força português, evita auto-detecção errada
        # - vad_filter=True: remove silêncios (Voice Activity Detection)
        # - condition_on_previous_text=False: evita loops repetitivos (CRÍTICO p/ PT-BR)
        # - temperature: fallback ladder, pega melhor resultado
        # - compression_ratio_threshold: rejeita transcrições com muita repetição
        # - log_prob_threshold: rejeita transcrições de baixa confiança
        # - no_speech_threshold: detecta silêncios prolongados
        segmentos, info = model.transcribe(
            str(arquivo),
            language=IDIOMA,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            initial_prompt="Transcrição em português brasileiro.",
        )

        # Junta os segmentos em texto único
        textos = []
        duracao_total = 0
        for seg in segmentos:
            textos.append(seg.text.strip())
            duracao_total = seg.end

        texto_final = " ".join(textos).strip()

        if not texto_final:
            print(f"   [AVISO] Transcrição vazia (áudio pode estar mudo ou ininteligível)")
            texto_final = "[Áudio sem fala detectada]"

        # Salva
        arquivo_saida.write_text(texto_final, encoding="utf-8")

        decorrido = time.time() - inicio
        ratio = duracao_total / decorrido if decorrido > 0 else 0
        print(f"   [OK]   → {arquivo_saida.name}")
        print(f"          Áudio: {duracao_total:.1f}s · Processamento: {decorrido:.1f}s · {ratio:.2f}x tempo real")
        print(f"          Idioma detectado: {info.language} (prob: {info.language_probability:.2f})")
        return True

    except Exception as e:
        print(f"   [ERRO] {arquivo.name}: {type(e).__name__}: {e}")
        return False


def main():
    imprimir_cabecalho()

    base = Path(__file__).resolve().parent
    pasta_entrada = base / PASTA_ENTRADA
    pasta_saida = base / PASTA_SAIDA
    pasta_saida.mkdir(parents=True, exist_ok=True)

    print(f" [INFO] Pasta de entrada: {pasta_entrada}")
    print(f" [INFO] Pasta de saída:   {pasta_saida}")
    print(f" [INFO] Modelo:           {MODELO}")
    print(f" [INFO] Idioma:           {IDIOMA}")
    print()

    # Detecta arquivos
    arquivos = encontrar_arquivos(pasta_entrada)
    if not arquivos:
        print(" [INFO] Nenhum arquivo de áudio encontrado na pasta 'entrada/'.")
        print(f"        Extensões aceitas: {', '.join(sorted(EXTENSOES_VALIDAS))}")
        print()
        input(" Pressione Enter para sair...")
        return 0

    print(f" [INFO] {len(arquivos)} arquivo(s) encontrado(s):")
    for f in arquivos:
        print(f"          - {f.name}")
    print()

    # Detecta device e carrega modelo
    device, compute = detectar_device_e_compute()
    print(f" [INFO] Carregando modelo '{MODELO}'... (primeira vez baixa do Hugging Face, ~3GB para large-v3)")
    print(f"        Próximas execuções serão instantâneas (cache local).")
    print()

    inicio_modelo = time.time()
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(MODELO, device=device, compute_type=compute)
    except Exception as e:
        print(f" [ERRO] Falha ao carregar modelo: {e}")
        print()
        print(" Possíveis causas:")
        print("   - Sem internet na primeira execução (precisa baixar o modelo)")
        print("   - Memória RAM insuficiente (large-v3 precisa ~5GB livres)")
        print("   - Tente um modelo menor: defina WHISPER_MODEL=medium ou small")
        print()
        input(" Pressione Enter para sair...")
        return 1

    print(f" [OK]   Modelo carregado em {time.time() - inicio_modelo:.1f}s")
    print()
    print(" " + "=" * 60)
    print("   PROCESSANDO ARQUIVOS")
    print(" " + "=" * 60)
    print()

    # Processa um a um
    inicio_total = time.time()
    sucessos = 0
    falhas = 0
    for i, arquivo in enumerate(arquivos, 1):
        print(f" [{i}/{len(arquivos)}]")
        if transcrever_arquivo(model, arquivo, pasta_saida):
            sucessos += 1
        else:
            falhas += 1
        print()

    # Resumo
    decorrido_total = time.time() - inicio_total
    print(" " + "=" * 60)
    print("   RESUMO")
    print(" " + "=" * 60)
    print(f" Total processado: {len(arquivos)}")
    print(f" Sucessos:         {sucessos}")
    print(f" Falhas:           {falhas}")
    print(f" Tempo total:      {decorrido_total:.1f}s")
    print(f" Saídas em:        {pasta_saida}")
    print()
    input(" Pressione Enter para sair...")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
