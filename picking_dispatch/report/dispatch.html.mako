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
<b>${_('Picked by')}: ${aggr.picker_id.name} &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ${_('Visa')}:_________________ <b>
<br/>
<br/>
<br/>
<table style="border:solid 1px" width="100%">
  <caption><b><u>${_('Products summary')}</u></b></caption>
  <tr></tr>
  <tr align="left">
    <th>${_('Product Code')}</th>
    <th>${_('Product')}</th>
    <th>${_('Carrier')}</th>
    <th>${_('QTY')}</th>
  </tr>  
  %for product, qty, carrier in aggr.product_quantity():
      <tr align="left">
        <td>${product.default_code}</td>
        <td>${product.name}</td>
        <td>${carrier}</td>
        <td>${qty}</td>
      </tr>
      <tr align="left">
        <td colspan="4"><pre class="description ">${product.description_warehouse and product.description_warehouse or ''}</pre></td>
      </tr>
  %endfor
</table>
%endfor
<br/>
</body>
</html>
