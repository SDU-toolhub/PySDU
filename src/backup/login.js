// 登录函数
function login(u, p, lt) {

  // 设置ul和pl的值
  $("#ul").val(u.length);
  $("#pl").val(p.length);
  // 设置rsa的值
  $("#rsa").val(strEnc(u + p + lt, "1", "2", "3"));

  // 获取设备指纹
  Fingerprint2.get(function (components) {
    var details = "";
    // 遍历组件，获取详细信息
    for (var index in components) {
      var obj = components[index];
      var line = obj.key + " = " + String(obj.value).substr(0, 100);
      details += line + "\n";
    }
    // 计算murmur值
    var murmur = Fingerprint2.x64hash128(
      components
        .map(function (pair) {
          return pair.value;
        })
        .join(),
      31
    );

    var details_s = "";
    // 遍历组件，获取详细信息
    for (var index in components) {
      var obj = components[index];
      // 跳过deviceMemory、screenResolution和availableScreenResolution
      if (
        obj.key == "deviceMemory" ||
        obj.key == "screenResolution" ||
        obj.key == "availableScreenResolution"
      ) {
        continue;
      }
      var line = obj.key + " = " + String(obj.value).substr(0, 100);
      details_s += line + "\n";
    }
    // 计算murmur_s和murmur_md5值
    var murmur_s = Fingerprint2.x64hash128(details_s, 31);
    var murmur_md5 = hex_md5(details_s);

    // 发送POST请求
    $.post(
      "device",
      {
        d: murmur,
        d_s: murmur_s,
        d_md5: murmur_md5,
        m: "1",
        u: strEnc(u, "1", "2", "3"),
        p: strEnc(p, "1", "2", "3"),
      },
      function (ret) {
        // 根据返回的信息进行处理
        if (ret.info == "validErr" || ret.info == "notFound") {
          location.reload();
        } else if (ret.info == "bind") {
          // 二次验证，绑定设备
          $("#phone").val(ret.m);
          phone(murmur_s, details_s);
        } else if (ret.info == "mobileErr") {
          // 手机有误
          $("#errormsg2").show().text("尚未绑定手机");
        } else if (ret.info == "binded" || ret.info == "pass") {
          // 直接提交
          $("#loginForm")[0].submit();
        }
      },
      "json"
    ).error(function (xhr, status, info) {
      if (is_weixin()) {
      }
    });
  });
}

function phone(murmur_s, details_s) {
  var win = layer.open({
    type: 1,
    title: "二次认证 ",
    content: $("#template_phone"),
    area: ["410px", "300px"],
  });

  $("#second_valid_ok")
    .unbind("click")
    .click(function () {
      var u = $("#un").val();
      var c = $("#mcode").val();
      if (!u) {
        layer.msg("用户名不能为空");
        return;
      }
      if (!c) {
        layer.msg("验证码不能为空  ");
        return;
      }
      $("#second_valid_ok").prop("disabled", "disabled");
      $.post(
        "device",
        {
          d: murmur_s,
          i: details_s,
          m: "3",
          u: u,
          c: c,
          s: $("#saveDevice").prop("checked") ? 1 : 0,
        },
        function (ret) {
          $("#second_valid_ok").prop("disabled", false);
          if (ret.info == "most") {
            layer.msg("设备已经超过最大数量,已自动解除最早一台授信设备。");
            setTimeout(function () {
              $("#loginForm")[0].submit();
            }, 1000);
          } else if (ret.info == "codeErr") {
            layer.msg("验证码有误");
          } else if (ret.info == "timeout") {
            layer.msg("验证码超时");
          } else if (ret.info == "ok") {
            $("#loginForm")[0].submit();
          } else {
            layer.msg("验证失败");
          }
        },
        "json"
      );
    });
}
