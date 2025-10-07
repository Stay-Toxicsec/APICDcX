function Initialize()
    dataFile = SKIN:GetVariable('DataFile')
    FontColorPos = SKIN:GetVariable('ColorPositive')
    FontColorNeg = SKIN:GetVariable('ColorNegative')
    FontColorText = SKIN:GetVariable('ColorNeutral')
    ColorUSDT = SKIN:GetVariable('ColorUSDT')
    ColorINR = SKIN:GetVariable('ColorINR')
end

function Update()
    local f = io.open(dataFile, "r")
    if not f then return "" end
    local idx = 1
    local maxLines = 5
    for line in f:lines() do
        local pair, usdt, inr, roe = string.match(line, "([^,]+),([^,]+),([^,]+),([^,]+)")
        if pair then
            usdt = tonumber(usdt)
            inr = tonumber(inr)
            roe = tonumber(roe)

            local isPositive = roe and roe > 0
            local lineColor = isPositive and FontColorPos or FontColorNeg
            local sign = (roe and roe > 0) and "+" or ""

            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'Pair', string.format('%-12s', pair))
            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'USDT', string.format('%0.2f USDT', usdt))
            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'INR', string.format('%d INR', inr))
            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'ROE', string.format('ROE: %s%0.2f%%', sign, roe))
            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'Color', lineColor)
            SKIN:Bang('!SetVariable', 'Line' .. idx .. 'Hidden', '0')

            idx = idx + 1
        end
        if idx > maxLines then break end
    end
    f:close()
    -- Clear and hide any leftover lines from previous updates
    for j = idx, maxLines do
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'Pair', '')
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'USDT', '')
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'INR', '')
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'ROE', '')
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'Color', FontColorText)
        SKIN:Bang('!SetVariable', 'Line' .. j .. 'Hidden', '1')
    end
    return ""
end

