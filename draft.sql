
SELECT stocks.symbol,sp.stock_id, sp.date, t.mx
FROM (
    SELECT stock_id, Max(close) AS mx
    FROM stockprices
    GROUP BY stock_id
) t JOIN stockprices sp ON sp.stock_id = t.stock_id AND t.mx=sp.close
JOIN stocks ON sp.stock_id=stocks.id
WHERE sp.date > '2022-03-14 05:00:00' 
;




subquery=session.query(func.max(close)).group_by(stock_id).filter_by(date >'2022-03-14 05:00:00').all()
stocks=session.query(Stock).filter(Stock.id.in_(subquery))