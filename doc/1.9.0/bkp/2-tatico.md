# CAMADA 2: TÁTICA (Score 0-100)
Quando agir? Define as codições táticas de compra/venda 

## INDICADORES DA CAMADA TÁTICA (TIMING OPERACIONAL)  
| Indicador       | Vender Forte (0) | Vender (20) | Hold (50) | Comprar (80) | Comprar Forte (100) |  
|-----------------|-------------------|-------------|-----------|--------------|----------------------|  
| **RSI Diário**  | > 85             | 70-85       | 30-70     | < 30         | < 25                |  
| **Volume Spot** | < 0.5x Média 30d | 0.5-0.8x    | 0.8-1.2x  | 1.2-1.5x     | > 1.5x              |  
| **Funding Rates**| > 0.1%          | 0.05-0.1%   | -0.05-0.05% | < -0.05%    | < -0.1%             |  
| **Delta OI**    | ↑ 30% em queda   | ↑ 15%       | Estável   | ↓ 15%        | ↓ 30% em alta       |  
| **Suporte/Resist**| < 2% do topo   | < 5% topo   | Neutro    | > 5% fundo   | > 10% fundo         |  


### CÁLCULO DO SCORE S3:  
1. Cada indicador contribui com **20%** (peso igual)  
2. Média aritmética simples dos 5 scores parciais

S3 = (RSI_score + Volume_score + Funding_score + DeltaOI_score + Suporte_score) / 5

### INTERPRETAÇÃO S3:
| S3     | Ação           | 
|--------|----------------|
| 80-100 | Comprar Forte  | 
| 60-79  | Comprar        | 
| 40-59  | Hold           | 
| 20-39  | Vender         | 
| 0-19   | Vender Forte   |