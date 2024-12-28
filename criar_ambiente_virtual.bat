
@echo off
setlocal

:: Verifique se um nome de ambiente foi fornecido
if "%~1"=="" (
    echo Uso: %0 nome_do_ambiente
    exit /b
)

:: Defina o nome do ambiente virtual a partir do argumento
set ENV_NAME=%~1

:: Verifique se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não está instalado. Por favor, instale o Python antes de continuar.
    exit /b
)

:: Crie o ambiente virtual
if not exist "%ENV_NAME%" (
    echo Criando o ambiente virtual "%ENV_NAME%"...
    python -m venv %ENV_NAME%
) else (
    echo O ambiente virtual "%ENV_NAME%" já existe.
)

:: Ativar o ambiente virtual
call "%ENV_NAME%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Falha ao ativar o ambiente virtual.
    exit /b
)

:: Instalar pacotes necessários
echo Instalando pacotes necessários...
pip install pytest

:: Mensagem de sucesso
echo Ambiente virtual "%ENV_NAME%" configurado com sucesso!
echo Para desativar o ambiente virtual, digite "deactivate".

:: Pausa para manter a janela aberta
pause
endlocal