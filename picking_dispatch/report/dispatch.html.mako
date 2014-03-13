<html>
<head>
<style type="text/css">
${css}
.description {
    font-family: helvetica;
    font-size: 9px;
}
</style>
</head>
<body>
<%from datetime import date %>
<table style="border:solid 0px" width="100%">
  <tr>
      <td align="left">${_('Date')}: ${formatLang(str(date.today()), date=True)}</td>
      <td align="right">${_('Printed by')}: ${user.name}  </td>
  </tr>  
</table>
<br/>
<br/>

%for aggr in objects:
<table style="border:solid 0px" width="100%">
  <tr> 
    <td colspan="2" align="center"><h1>${_('Dispatch Order')} ${aggr.dispatch_name}</h1></td>
  </tr>
  <tr>
     <td> <br /><b>${_('Picked by')}: ${aggr.picker_id.name} &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ${_('Visa')}:_________________ <b></td>
   </tr>
</table>
<br/>
<br/>
<p>${aggr.dispatch_notes}</p>
<br/>

<%
    # check if column 'Variant' must be displayed
    display_variants = False
    for locations, product_quantities in aggr.iter_locations():
        for product, qty, carrier in product_quantities:
            if product.variants:
                display_variants = True
                break
        else:
            continue
        break
%>
%for locations, product_quantities in aggr.iter_locations():
<table style="border:solid 1px" width="100%">
  <caption><b><u>${locations[0]} &#x21E8; ${locations[1]}</u></b></caption>
  <tr></tr>
  <tr align="left">
    <th>${_('Product Code')}</th>
    <th>${_('Product')}</th>
    %if display_variants:
        <th>${_('Variant')}</th>
    %endif
    <th>${_('Carrier')}</th>
    <th>${_('QTY')}</th>
    <th>${_('Explanation')}</th>
  </tr>  
  %for product, qty, carrier in product_quantities:
      <tr align="left">
        <td>${product.default_code}</td>
        <td>${product.name}</td>
        %if display_variants:
            <td>
                %if product.variants:
                  ${product.variants}
                %else:
                  ${'-'}
                %endif
            </td>
        %endif
        <td>${carrier}</td>
        <td>${qty}</td>
        <td>${_('stock error')}<br/>${_('breakage')}</td>
      </tr>
      <tr align="left">
        <td colspan="4"><pre class="description ">${product.description_warehouse and product.description_warehouse or ''}</pre></td>
      </tr>
  %endfor
</table>
%endfor
        <p style="page-break-after:always">&nbsp</>
%endfor
</body>
</html>
