
const axios = require('axios');
const fs = require('fs');
const { format, isTuesday, isWednesday, isThursday, isFriday, isSaturday, addDays } = require('date-fns');
const { ptBR } = require('date-fns/locale');
const holidays = require('date-holidays');
const path = require('path');

const logDir = 'D:\\juliap\\Documents\\JavaScript\\Cotação de Moedas\\Logs de Execução';
const currentDateTime = new Date();
const formattedTime = format(currentDateTime, "ddMMyyyy_HHmm");
const logFilePath = path.join(logDir, `log_${formattedTime}.txt`);

function log(message) {
    const timestamp = format(new Date(), "yyyy-MM-dd HH:mm:ss");
    fs.appendFileSync(logFilePath, `${timestamp}: ${message}\n`);
}

async function fetchCurrencyRate() {
    const hd = new holidays('BR');
    if ([1, 2, 3, 4, 5].includes(currentDateTime.getDay()) && !hd.isHoliday(currentDateTime)) {
        log("Validado o dia de execução. Seguindo com o processo...");

        const today = new Date();
        const tomorrow = addDays(today, 1);
        const data_ini = format(today, "dd/MM/yyyy", { locale: ptBR });
        const data_fim = format(tomorrow, "dd/MM/yyyy", { locale: ptBR });

        try {
            const urlYuan = `https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=178&DATAINI=${data_ini}&DATAFIM=${data_fim}`;
            const responseYuan = await axios.get(urlYuan);
            if (responseYuan.status) {
                fs.writeFileSync('cotacao_yuan.txt', responseYuan.data);
                log("Arquivo de cotação Yuan salvo.");
            }

            const urlSelic = `https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados?formato=json&dataInicial=${data_ini}&dataFinal=${data_ini}`;
            const responseSelic = await axios.get(urlSelic);
            if (responseSelic.status) {
                fs.writeFileSync('cotacao_selic.txt', JSON.stringify(responseSelic.data));
                log("Arquivo de taxa Selic salvo.");
            }
        } catch (error) {
            log(`Erro durante as requisições de API: ${error}`);
        }
    } else {
        log("Hoje é domingo, segunda-feira ou feriado. O script não será executado.");
    }

    log("Execução do script finalizada.");
}

fetchCurrencyRate();
